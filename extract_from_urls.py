"""
Lee un Excel/CSV con URLs y extrae para cada URL:
- nombre de la inmobiliaria (H1, texto antes de la coma si aplica)
- total de inmuebles (texto como "Mostrando 1-10 de 123")

Uso:
python extract_from_urls.py urls.xlsx --column url
python extract_from_urls.py urls.csv

Si la extracción por HTTP falla para obtener el número, el script intentará con Selenium (headless).
"""
import argparse
import os
import re
import time
import json
from datetime import datetime
import signal

import requests
from bs4 import BeautifulSoup

# Opcionales
try:
    import pandas as pd
except Exception:
    pd = None

# Selenium fallback
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except Exception:
    SELENIUM_AVAILABLE = False

RESULTS_DIR = 'resultados'
os.makedirs(RESULTS_DIR, exist_ok=True)


def save_results(results, prefix='extraction'):
    """Guarda CSV y JSON en RESULTS_DIR con prefijo y timestamp."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = os.path.join(RESULTS_DIR, f'{prefix}_{timestamp}.csv')
    json_file = os.path.join(RESULTS_DIR, f'{prefix}_{timestamp}.json')
    try:
        import csv as _csv
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = _csv.DictWriter(f, fieldnames=['url', 'titulo', 'cantidad_inmuebles'])
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print('Error guardando CSV:', e)
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print('Error guardando JSON:', e)
    return csv_file, json_file


def save_partial(results):
    """Guardar un archivo parcial 'latest' (sobrescribe) y también un archivo timestamped."""
    latest_csv = os.path.join(RESULTS_DIR, 'extraction_partial_latest.csv')
    latest_json = os.path.join(RESULTS_DIR, 'extraction_partial_latest.json')
    try:
        import csv as _csv
        with open(latest_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = _csv.DictWriter(f, fieldnames=['url', 'titulo', 'cantidad_inmuebles'])
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print('Error guardando partial CSV latest:', e)
    try:
        with open(latest_json, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print('Error guardando partial JSON latest:', e)

    # timestamped archive
    try:
        _csv, _json = save_results(results, prefix='extraction_partial')
        return latest_csv, latest_json, _csv, _json
    except Exception:
        return latest_csv, latest_json, None, None


def _signal_handler(sig, frame):
    # placeholder; will be set in main closure where 'results' is known
    print('\nInterrupción (signal) detectada. Intentando guardar parciales...')


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

PATTERNS = [
    re.compile(r'Mostrando\s*\d+\s*[-–—]\s*\d+\s*de\s*(\d+)', re.IGNORECASE),
    re.compile(r'Mostrando\s*\d+\s*al\s*\d+\s*de\s*(\d+)', re.IGNORECASE),
    re.compile(r'Mostrando\s*\d+\s*de\s*(\d+)', re.IGNORECASE),
    re.compile(r'1\s*[-–—]\s*\d+\s*de\s*(\d+)', re.IGNORECASE),
    re.compile(r'de\s*(\d+)\s*resultados', re.IGNORECASE),
    re.compile(r'de\s*(\d+)\s*anuncios', re.IGNORECASE),
    re.compile(r'(\d+)\s*(inmueble|inmuebles|propiedad|anuncio)s?', re.IGNORECASE),
]


KEYWORD_SPLIT = [
    'Apartamentos', 'Casas', 'Inmuebles', 'inmuebles', 'Venta', 'Arriendo', 'Venta y Arriendo',
    'en Venta', 'en Arriendo', 'en Colombia'
]


def extract_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Extract H1
    def clean_name(text):
        if not text:
            return None
        # quitar contenido entre paréntesis
        text = re.sub(r"\(.*?\)", "", text).strip()
        # dividir por guiones, barras u otros separadores comunes
        parts = re.split(r"[-–—|\|]", text)
        text = parts[0].strip()
        # dividir por keywords comunes (ej: 'Apartamentos', 'Casas', 'Inmuebles'...) y tomar la parte izquierda
        for kw in KEYWORD_SPLIT:
            if kw in text:
                text = text.split(kw)[0].strip()
        # quitar sufijos como 'Fincaraiz' u otras redundancias
        text = re.sub(r"Fincaraiz.*$", "", text, flags=re.IGNORECASE).strip()
        # eliminar comas finales
        text = re.sub(r"\,$", "", text).strip()
        return text or None

    nombre = None
    h1 = soup.find('h1')
    if h1:
        texto = h1.get_text(separator=' ', strip=True)
        nombre = clean_name(texto)

    # Si no hay h1, intentar meta og:title, title
    if not nombre:
        meta_og = soup.find('meta', property='og:title')
        if meta_og and meta_og.get('content'):
            nombre = clean_name(meta_og.get('content'))

    if not nombre:
        meta_title = soup.find('meta', attrs={'name': 'title'})
        if meta_title and meta_title.get('content'):
            nombre = clean_name(meta_title.get('content'))

    if not nombre:
        title_tag = soup.find('title')
        if title_tag:
            nombre = clean_name(title_tag.get_text(strip=True))

    if not nombre:
        nombre = 'No disponible'

    # Buscar el texto que contenga 'Mostrando' o patrón
    texto_total = soup.get_text(separator=' ', strip=True)
    total_inmuebles = None

    # Priorizar fragmento corto que contenga la palabra 'Mostrando' para acelerar matching
    snippet = ''
    idx = texto_total.lower().find('mostrando')
    if idx != -1:
        snippet = texto_total[max(0, idx - 100): idx + 200]
    else:
        snippet = texto_total[:1000]

    for pat in PATTERNS:
        m = pat.search(snippet)
        if m:
            try:
                total_inmuebles = int(re.sub(r"\D", "", m.group(1)))
            except Exception:
                total_inmuebles = None
            if total_inmuebles is not None:
                break

    # También buscar elementos específicos que puedan contener el conteo
    if total_inmuebles is None:
        possible_selectors = ['.ant-list', '.inmuebles-count', '.property-count', '.count-inmuebles']
        for sel in possible_selectors:
            el = soup.select_one(sel)
            if el:
                text = el.get_text(' ', strip=True)
                for pat in PATTERNS:
                    m = pat.search(text)
                    if m:
                        try:
                            total_inmuebles = int(re.sub(r"\D", "", m.group(1)))
                        except:
                            total_inmuebles = None
                        if total_inmuebles:
                            break
            if total_inmuebles:
                break

    if total_inmuebles is None:
        total_inmuebles = 0

    return nombre, total_inmuebles


def fetch_requests(url, timeout=12):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r.text
    except Exception as e:
        return None


def fetch_selenium(url, headless=True, timeout=10):
    if not SELENIUM_AVAILABLE:
        return None
    options = Options()
    if headless:
        options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(timeout)
        driver.get(url)
        time.sleep(2)
        html = driver.page_source
        return html
    except Exception:
        return None
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass


def read_urls(input_path, column_name=None):
    urls = []
    if input_path.lower().endswith(('.xls', '.xlsx')):
        if pd is None:
            raise RuntimeError('Pandas no está instalado. Instálalo o pasa un CSV con URLs.')
        df = pd.read_excel(input_path)
        if column_name and column_name in df.columns:
            urls = df[column_name].dropna().astype(str).tolist()
        else:
            # intentar adivinar columna
            for col in ['url', 'URL', 'link', 'Link', 'href']:
                if col in df.columns:
                    urls = df[col].dropna().astype(str).tolist()
                    break
            if not urls:
                # tomar la primera columna
                urls = df.iloc[:, 0].dropna().astype(str).tolist()
    else:
        # CSV o TXT
        if pd is not None and input_path.lower().endswith('.csv'):
            df = pd.read_csv(input_path)
            if column_name and column_name in df.columns:
                urls = df[column_name].dropna().astype(str).tolist()
            else:
                for col in ['url', 'URL', 'link', 'Link', 'href']:
                    if col in df.columns:
                        urls = df[col].dropna().astype(str).tolist()
                        break
                if not urls:
                    urls = df.iloc[:, 0].dropna().astype(str).tolist()
        else:
            # plain text file, one url per line
            with open(input_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        urls.append(line)
    # Normalizar URLs
    urls = [u if u.startswith('http') else 'https://www.fincaraiz.com.co' + (u if u.startswith('/') else '/' + u) for u in urls]
    return urls


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Ruta a archivo Excel/CSV/TXT con URLs (o una sola URL)')
    parser.add_argument('--column', help='Nombre de la columna que contiene las URLs (opcional)')
    parser.add_argument('--force-selenium', action='store_true', help='Forzar uso de Selenium para todas las URLs')
    parser.add_argument('--start-index', type=int, default=1, help='Índice (1-based) desde el que empezar/procesar (útil para reanudar)')
    parser.add_argument('--save-every', type=int, default=200, help='Guardar resultados parciales cada N URLs procesadas')
    parser.add_argument('--headless', action='store_true', help='Usar Selenium en modo headless (si se usa)')
    args = parser.parse_args()

    input_path = args.input

    # Si el input es una única URL
    urls = []
    if input_path.startswith('http'):
        urls = [input_path]
    else:
        urls = read_urls(input_path, args.column)

    results = []
    start_idx = max(1, int(args.start_index))
    save_every = max(1, int(args.save_every))

    # Registrar handler de señal para guardar parciales si el usuario interrumpe (Ctrl+C)
    def _handler(sig, frame):
        print('\nInterrupción detectada (signal). Guardando resultados parciales...')
        try:
            latest_csv, latest_json, archived_csv, archived_json = save_partial(results)
            print(f'  ✓ Parcial guardado: {latest_csv} (archivado: {archived_csv})')
        except Exception as e:
            print('  ⚠️ Error guardando parcial en handler:', e)
        raise KeyboardInterrupt()

    signal.signal(signal.SIGINT, _handler)

    try:
        for idx, url in enumerate(urls, 1):
            if idx < start_idx:
                continue
            print(f'[{idx}/{len(urls)}] Procesando: {url}')
            html = None
            if not args.force_selenium:
                html = fetch_requests(url)
            if not html:
                print('  -> Requests falló o no encontró datos. Intentando con Selenium...')
                html = fetch_selenium(url, headless=args.headless)
                if not html:
                    print('  -> Selenium falló o no disponible. Registrando valores por defecto.')
                    nombre, total = ('No disponible', 0)
                    results.append({'url': url, 'titulo': nombre, 'cantidad_inmuebles': total})
                    # guarda parcial si toca
                    if (len(results) % save_every) == 0:
                        latest_csv, latest_json, archived_csv, archived_json = save_partial(results)
                        print(f'  ✓ Guardado parcial en {latest_csv} (archivo de archivo: {archived_csv})')
                    continue
            nombre, total = extract_from_html(html)
            results.append({'url': url, 'titulo': nombre, 'cantidad_inmuebles': total})
            # Guardado parcial periódico
            if (len(results) % save_every) == 0:
                latest_csv, latest_json, archived_csv, archived_json = save_partial(results)
                print(f'  ✓ Guardado parcial en {latest_csv} (archivo de archivo: {archived_csv})')
    except KeyboardInterrupt:
        print('\nInterrupción detectada. Guardando resultados parciales antes de salir...')
        try:
            latest_csv, latest_json, archived_csv, archived_json = save_partial(results)
            print(f'  ✓ Parcial guardado: {latest_csv} (archivado: {archived_csv})')
        except Exception as e:
            print('  ⚠️ Error guardando parcial:', e)
    except Exception as e:
        print('\nError durante el procesamiento:', e)
        try:
            latest_csv, latest_json, archived_csv, archived_json = save_partial(results)
            print(f'  ✓ Parcial guardado debido a error: {latest_csv}')
        except Exception as e2:
            print('  ⚠️ Error guardando parcial tras excepción:', e2)

    # Guardar resultados
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = os.path.join(RESULTS_DIR, f'extraction_{timestamp}.csv')
    json_file = os.path.join(RESULTS_DIR, f'extraction_{timestamp}.json')

    try:
        import csv as _csv
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = _csv.DictWriter(f, fieldnames=['url', 'titulo', 'cantidad_inmuebles'])
            writer.writeheader()
            writer.writerows(results)
        print(f'✓ Resultados guardados en {csv_file}')
    except Exception as e:
        print('Error guardando CSV:', e)

    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f'✓ Resultados guardados en {json_file}')
    except Exception as e:
        print('Error guardando JSON:', e)

if __name__ == '__main__':
    main()
