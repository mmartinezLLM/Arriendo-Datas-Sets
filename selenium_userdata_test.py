"""
Prueba de extracción de teléfono usando Selenium sin remote debugging.
Conecta a Chrome usando el user-data-dir (perfil del navegador).

Antes de ejecutar: CIERRA CHROME completamente.
"""
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Localizar el perfil de Chrome del usuario
CHROME_USER_DATA = r"C:\Users\Miguel Martinez SSD\AppData\Local\Google\Chrome\User Data"
CHROME_PROFILE = "Default"

print(f"Conectando a Chrome con profile: {CHROME_PROFILE}")
print(f"User Data Dir: {CHROME_USER_DATA}")

opts = Options()
opts.add_argument(f"--user-data-dir={CHROME_USER_DATA}")
opts.add_argument(f"--profile-directory={CHROME_PROFILE}")
opts.add_argument("--disable-blink-features=AutomationControlled")
opts.add_experimental_option("excludeSwitches", ["enable-automation"])
opts.add_experimental_option('useAutomationExtension', False)

try:
    print("\nIniciando Chrome...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    print("✓ Chrome iniciado correctamente")
    
    # Ir a una URL de prueba
    test_url = "https://www.fincaraiz.com.co/inmobiliarias/perfil/176359705"
    print(f"\nAbriendo: {test_url}")
    driver.get(test_url)
    time.sleep(3)  # Esperar a que cargue la página
    
    print(f"✓ Página cargada")
    print(f"  Título: {driver.title}")
    print(f"  URL actual: {driver.current_url}")
    
    # Intentar encontrar el número de teléfono
    print("\n[Buscando teléfono...]")
    try:
        # Buscar enlace de teléfono
        phone_link = driver.find_element(By.XPATH, "//a[contains(@href, 'tel:')]")
        phone_text = phone_link.text
        phone_href = phone_link.get_attribute('href')
        print(f"✓ Teléfono encontrado: {phone_text}")
        print(f"  Href: {phone_href}")
    except Exception as e:
        print(f"  No se encontró enlace tel: {e}")
        
        # Intentar alternativas
        try:
            phone_span = driver.find_element(By.XPATH, "//*[contains(text(), '+57') or contains(text(), '3')]//ancestor::*[1]")
            print(f"  Elemento con número: {phone_span.text}")
        except:
            print("  No se encontró número telefónico en la página")
    
    driver.quit()
    print("\n✓ PRUEBA COMPLETADA EXITOSAMENTE")
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
