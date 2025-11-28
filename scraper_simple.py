"""
Script simplificado para scraping de inmobiliarias fincaraiz.com.co
Versión sin dependencias problemáticas
"""
import time
import os
import json
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

# Crear carpeta de resultados
os.makedirs('resultados', exist_ok=True)

def log_msg(msg):
    """Imprime y guarda logs"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg)
    with open('resultados/scraper.log', 'a', encoding='utf-8') as f:
        f.write(full_msg + '\n')

def inicializar_navegador():
    """Inicializa el navegador Chrome"""
    log_msg("Inicializando navegador Chrome...")
    
    options = ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    
    log_msg("✓ Navegador inicializado correctamente")
    return driver

def extraer_inmobiliarias(driver):
    """Extrae información de las inmobiliarias"""
    log_msg("Accediendo a fincaraiz.com.co...")
    
    url = "https://www.fincaraiz.com.co/inmobiliarias/"
    driver.get(url)
    
    log_msg("Esperando carga de página...")
    time.sleep(5)
    
    log_msg("Analizando estructura de la página...")
    
    # Obtener HTML
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    # Buscar elementos de inmobiliarias
    inmobiliarias = []
    
    # Estrategia 1: Buscar por clases comunes
    elementos = soup.find_all('div', class_=lambda x: x and ('company' in x.lower() or 'card' in x.lower()))
    
    if not elementos:
        log_msg("Buscando por estructura alternativa...")
        elementos = soup.find_all('article')
    
    if not elementos:
        log_msg("Buscando por data-testid...")
        elementos = soup.find_all(attrs={'data-testid': lambda x: x and 'company' in str(x).lower()})
    
    log_msg(f"Se encontraron {len(elementos)} elementos potenciales")
    
    for idx, elemento in enumerate(elementos[:20], 1):  # Limitar a 20 para testing
        try:
            datos = extraer_datos_elemento(elemento)
            if datos and any(datos.values()):
                inmobiliarias.append(datos)
                log_msg(f"[{idx}] {datos.get('titulo', 'Sin nombre')}")
        except Exception as e:
            log_msg(f"Error en elemento {idx}: {str(e)}")
            continue
    
    log_msg(f"\n✓ Total extraído: {len(inmobiliarias)} inmobiliarias")
    return inmobiliarias

def extraer_datos_elemento(elemento):
    """Extrae datos de un elemento de inmobiliaria"""
    try:
        datos = {
            'titulo': extraer_texto(elemento, ['h2', 'h3', '.nombre', '.company-name']),
            'correo': extraer_texto(elemento, ['a[href^="mailto:"]', '.email', '.correo']),
            'telefono': extraer_texto(elemento, ['.telefono', '.phone', 'a[href^="tel:"]']) or 'No disponible',
            'cantidad_inmuebles': extraer_numero(elemento, ['.count', '.cantidad', '[data-count]']),
            'url': extraer_url(elemento, ['a[href]'])
        }
        return datos
    except:
        return None

def extraer_texto(elemento, selectores):
    """Extrae texto de un elemento"""
    from bs4 import BeautifulSoup
    if isinstance(elemento, str):
        soup = BeautifulSoup(elemento, 'html.parser')
    else:
        soup = elemento
    
    for selector in selectores:
        try:
            if selector.startswith('['):
                elemento_encontrado = soup.select_one(selector)
            elif selector.startswith('.'):
                elemento_encontrado = soup.find(class_=selector[1:])
            else:
                elemento_encontrado = soup.find(selector)
            
            if elemento_encontrado:
                texto = elemento_encontrado.get_text(strip=True)
                if texto:
                    return texto
        except:
            continue
    
    return 'No disponible'

def extraer_numero(elemento, selectores):
    """Extrae número de un elemento"""
    from bs4 import BeautifulSoup
    import re
    
    if isinstance(elemento, str):
        soup = BeautifulSoup(elemento, 'html.parser')
    else:
        soup = elemento
    
    for selector in selectores:
        try:
            elemento_encontrado = soup.select_one(selector) if selector.startswith('[') else soup.find(class_=selector[1:])
            if elemento_encontrado:
                texto = elemento_encontrado.get_text(strip=True)
                numeros = re.findall(r'\d+', texto)
                if numeros:
                    return int(numeros[0])
        except:
            continue
    
    return 0

def extraer_url(elemento, selectores):
    """Extrae URL de un elemento"""
    from bs4 import BeautifulSoup
    
    if isinstance(elemento, str):
        soup = BeautifulSoup(elemento, 'html.parser')
    else:
        soup = elemento
    
    for selector in selectores:
        try:
            elemento_encontrado = soup.select_one(selector)
            if elemento_encontrado:
                href = elemento_encontrado.get('href', '')
                if href:
                    if href.startswith('http'):
                        return href
                    elif href.startswith('/'):
                        return "https://www.fincaraiz.com.co" + href
        except:
            continue
    
    return 'No disponible'

def guardar_resultados(inmobiliarias):
    """Guarda los resultados en CSV y JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Guardar en CSV
    csv_file = f'resultados/inmobiliarias_{timestamp}.csv'
    log_msg(f"Guardando en CSV: {csv_file}")
    
    if inmobiliarias:
        try:
            import pandas as pd
            df = pd.DataFrame(inmobiliarias)
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            log_msg(f"✓ CSV guardado: {csv_file}")
        except:
            # Fallback sin pandas
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                if inmobiliarias:
                    writer = csv.DictWriter(f, fieldnames=inmobiliarias[0].keys())
                    writer.writeheader()
                    writer.writerows(inmobiliarias)
            log_msg(f"✓ CSV guardado (sin pandas): {csv_file}")
    
    # Guardar en JSON
    json_file = f'resultados/inmobiliarias_{timestamp}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(inmobiliarias, f, ensure_ascii=False, indent=2)
    log_msg(f"✓ JSON guardado: {json_file}")
    
    # Mostrar resumen
    log_msg("\n" + "="*70)
    log_msg("RESUMEN DE EXTRACCIÓN")
    log_msg("="*70)
    log_msg(f"Total de inmobiliarias: {len(inmobiliarias)}")
    log_msg(f"Con correo: {len([x for x in inmobiliarias if x.get('correo') != 'No disponible'])}")
    log_msg(f"Total inmuebles: {sum(x.get('cantidad_inmuebles', 0) for x in inmobiliarias)}")
    log_msg("="*70)

def main():
    """Función principal"""
    driver = None
    
    try:
        log_msg("="*70)
        log_msg("INICIANDO SCRAPER DE INMOBILIARIAS")
        log_msg("="*70)
        
        # Inicializar navegador
        driver = inicializar_navegador()
        
        # Extraer inmobiliarias
        inmobiliarias = extraer_inmobiliarias(driver)
        
        # Guardar resultados
        if inmobiliarias:
            guardar_resultados(inmobiliarias)
        else:
            log_msg("⚠️ No se extrajeron inmobiliarias")
        
        log_msg("✓ SCRAPER COMPLETADO")
        log_msg("="*70)
    
    except Exception as e:
        log_msg(f"❌ ERROR: {str(e)}")
        import traceback
        log_msg(traceback.format_exc())
    
    finally:
        if driver:
            log_msg("Cerrando navegador...")
            driver.quit()

if __name__ == "__main__":
    main()
