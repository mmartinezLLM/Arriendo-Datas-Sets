"""
Prueba simple de Selenium: abre Chrome, navega a una página de prueba
sin requeririr remote debugging ni perfiles específicos.
"""
import os
import time
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Crear un directorio temporal para este Chrome instance
temp_profile = tempfile.mkdtemp()
print(f"Usando perfil temporal: {temp_profile}\n")

opts = Options()
opts.add_argument(f"--user-data-dir={temp_profile}")
opts.add_argument("--disable-blink-features=AutomationControlled")
opts.add_experimental_option("excludeSwitches", ["enable-automation"])
opts.add_experimental_option('useAutomationExtension', False)
opts.add_argument("--disable-notifications")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")

try:
    print("[1] Iniciando Chrome...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    print("✓ Chrome iniciado correctamente\n")
    
    # Ir a una URL de prueba
    test_url = "https://www.fincaraiz.com.co/inmobiliarias/perfil/176359705"
    print(f"[2] Abriendo URL: {test_url}")
    driver.get(test_url)
    
    # Esperar a que cargue
    print("    Esperando carga...")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))
    time.sleep(2)
    
    print(f"✓ Página cargada")
    print(f"  - Título: {driver.title}")
    print(f"  - URL: {driver.current_url}\n")
    
    # Buscar información
    print("[3] Buscando datos en la página...")
    html_snippet = driver.page_source[:500]
    print(f"  HTML inicial: {html_snippet}...\n")
    
    # Buscar teléfono
    print("[4] Buscando número telefónico...")
    try:
        phone_element = driver.find_element(By.XPATH, "//a[contains(@href, 'tel:')]")
        phone_text = phone_element.text
        phone_href = phone_element.get_attribute('href')
        print(f"✓ Teléfono encontrado!")
        print(f"  - Texto: {phone_text}")
        print(f"  - Href: {phone_href}")
    except Exception as e:
        print(f"  Búsqueda de 'tel:' falló: {e}")
        # Intentar una búsqueda más genérica
        body_text = driver.find_element(By.TAG_NAME, "body").text
        if "+57" in body_text or "3" in body_text[:100]:
            print(f"  ✓ Posible número encontrado en el HTML")
    
    driver.quit()
    print("\n✓ PRUEBA COMPLETADA")
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}")
    print(f"Mensaje: {e}")
