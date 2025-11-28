"""
Scraper mejorado para fincaraiz.com.co/inmobiliarias
Extrae: título, correo, teléfono, cantidad de inmuebles
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json
import csv
from datetime import datetime
import os

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
    
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    
    log_msg("✓ Navegador inicializado")
    return driver

def extraer_inmobiliarias(driver):
    """Extrae todas las inmobiliarias de la página"""
    log_msg("Accediendo a fincaraiz.com.co/inmobiliarias...")
    
    url = "https://www.fincaraiz.com.co/inmobiliarias"
    driver.get(url)
    
    log_msg("Esperando carga de página...")
    time.sleep(6)
    
    inmobiliarias = []
    
    # Esperar a que los items estén presentes
    log_msg("Buscando elementos inmobiliarias...")
    wait = WebDriverWait(driver, 20)
    
    try:
        # Buscar todos los links de inmobiliarias (están en los hrefs)
        elementos_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/inmobiliarias/']")
        log_msg(f"Encontrados {len(elementos_links)} links de inmobiliarias")
        
        # Extraer URLs únicas
        urls = set()
        for elem in elementos_links:
            href = elem.get_attribute('href')
            if href and '/inmobiliarias/-' in href and href not in urls:
                urls.add(href)
        
        log_msg(f"Total de URLs únicas: {len(urls)}")
        
        # Procesar cada URL
        for idx, url_inmobiliaria in enumerate(list(urls)[:50], 1):  # Limitar a 50 para test
            try:
                log_msg(f"\n[{idx}] Accediendo a: {url_inmobiliaria[:60]}...")
                driver.get(url_inmobiliaria)
                time.sleep(2)
                
                datos = extraer_datos_pagina_inmobiliaria(driver, url_inmobiliaria)
                if datos:
                    inmobiliarias.append(datos)
                    log_msg(f"  ✓ Extraído: {datos['titulo']}")
                    log_msg(f"    Correo: {datos['correo']}")
                    log_msg(f"    Teléfono: {datos['telefono']}")
                    log_msg(f"    Inmuebles: {datos['cantidad_inmuebles']}")
            
            except Exception as e:
                log_msg(f"  ✗ Error: {str(e)}")
                continue
        
        log_msg(f"\n✓ Total extraído: {len(inmobiliarias)} inmobiliarias")
        return inmobiliarias
    
    except Exception as e:
        log_msg(f"Error obteniendo elementos: {str(e)}")
        return []

def extraer_datos_pagina_inmobiliaria(driver, url):
    """Extrae datos de una página de inmobiliaria"""
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extraer título
        titulo = extraer_titulo(soup)
        
        # Extraer correo
        correo = extraer_correo(soup)
        
        # Extraer teléfono
        telefono = extraer_telefono(soup)
        
        # Extraer cantidad de inmuebles
        cantidad = extraer_cantidad_inmuebles(soup)
        
        datos = {
            'titulo': titulo,
            'correo': correo,
            'telefono': telefono,
            'cantidad_inmuebles': cantidad,
            'url': url
        }
        
        return datos if any(datos.values()) else None
    
    except Exception as e:
        log_msg(f"  Error extrayendo datos: {str(e)}")
        return None

def extraer_titulo(soup):
    """Extrae el título de la inmobiliaria"""
    selectores = [
        'h1',
        'h2',
        '.company-name',
        '.company-title',
        '[data-testid="companyName"]',
        '.inmobiliaria-nombre'
    ]
    
    for selector in selectores:
        try:
            elem = soup.select_one(selector)
            if elem:
                texto = elem.get_text(strip=True)
                if texto and len(texto) > 2:
                    return texto
        except:
            pass
    
    return 'No disponible'

def extraer_correo(soup):
    """Extrae el correo de la inmobiliaria"""
    # Buscar enlaces de correo
    elementos_correo = soup.find_all('a', href=lambda x: x and 'mailto:' in x)
    
    for elem in elementos_correo:
        correo = elem.get_text(strip=True)
        if '@' in correo:
            return correo
    
    # Buscar en texto
    import re
    patron_email = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(patron_email, soup.get_text())
    if emails:
        return emails[0]
    
    return 'No disponible'

def extraer_telefono(soup):
    """Extrae el teléfono de la inmobiliaria"""
    # Buscar enlaces de teléfono
    elementos_tel = soup.find_all('a', href=lambda x: x and 'tel:' in x)
    
    for elem in elementos_tel:
        telefono = elem.get_text(strip=True)
        if telefono:
            return telefono
    
    # Buscar en texto números telefónicos
    import re
    patron_tel = r'(\+?\d{1,3}?\s?)?\d{1,4}[\s\-]?\d{1,4}[\s\-]?\d{1,9}'
    telefonos = re.findall(patron_tel, soup.get_text())
    if telefonos:
        return telefonos[0]
    
    # Ver si hay botón de revelar teléfono
    botones = soup.find_all('button')
    for btn in botones:
        texto = btn.get_text(strip=True).lower()
        if 'teléfono' in texto or 'llamar' in texto or 'mostrar' in texto:
            return 'Requiere clic (interactivo)'
    
    return 'No disponible'

def extraer_cantidad_inmuebles(soup):
    """Extrae la cantidad de inmuebles"""
    import re
    
    # Buscar en textos comunes
    selectores = [
        '.property-count',
        '.count-inmuebles',
        '[data-testid="propertyCount"]',
        '.inmuebles-count'
    ]
    
    for selector in selectores:
        try:
            elem = soup.select_one(selector)
            if elem:
                texto = elem.get_text(strip=True)
                numeros = re.findall(r'\d+', texto)
                if numeros:
                    return int(numeros[0])
        except:
            pass
    
    # Buscar en todo el texto por patrones
    texto_completo = soup.get_text()
    # Patrones como "123 inmuebles", "123 propiedades", etc
    patrones = [
        r'(\d+)\s+inmueble',
        r'(\d+)\s+propiedad',
        r'(\d+)\s+anuncio'
    ]
    
    for patron in patrones:
        matches = re.findall(patron, texto_completo.lower())
        if matches:
            return int(matches[0])
    
    return 0

def guardar_resultados(inmobiliarias):
    """Guarda los resultados en CSV y JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # CSV
    csv_file = f'resultados/inmobiliarias_{timestamp}.csv'
    log_msg(f"\nGuardando en CSV: {csv_file}")
    
    if inmobiliarias:
        try:
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=['titulo', 'correo', 'telefono', 'cantidad_inmuebles', 'url'])
                writer.writeheader()
                writer.writerows(inmobiliarias)
            log_msg(f"✓ CSV guardado")
        except Exception as e:
            log_msg(f"Error guardando CSV: {e}")
    
    # JSON
    json_file = f'resultados/inmobiliarias_{timestamp}.json'
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(inmobiliarias, f, ensure_ascii=False, indent=2)
        log_msg(f"✓ JSON guardado: {json_file}")
    except Exception as e:
        log_msg(f"Error guardando JSON: {e}")
    
    # Resumen
    log_msg("\n" + "="*70)
    log_msg("RESUMEN FINAL")
    log_msg("="*70)
    log_msg(f"Total extraído: {len(inmobiliarias)} inmobiliarias")
    log_msg(f"Con correo: {len([x for x in inmobiliarias if x.get('correo') != 'No disponible'])}")
    log_msg(f"Con teléfono: {len([x for x in inmobiliarias if x.get('telefono') != 'No disponible' and 'interactivo' not in x.get('telefono', '').lower()])}")
    log_msg(f"Total inmuebles: {sum(x.get('cantidad_inmuebles', 0) for x in inmobiliarias)}")
    log_msg("="*70)

def main():
    """Función principal"""
    driver = None
    
    try:
        log_msg("="*70)
        log_msg("SCRAPER DE INMOBILIARIAS - FINCARAIZ.COM.CO")
        log_msg("="*70)
        
        driver = inicializar_navegador()
        inmobiliarias = extraer_inmobiliarias(driver)
        
        if inmobiliarias:
            guardar_resultados(inmobiliarias)
        else:
            log_msg("⚠️ No se extrajeron inmobiliarias")
        
        log_msg("✓ SCRAPER COMPLETADO")
    
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
