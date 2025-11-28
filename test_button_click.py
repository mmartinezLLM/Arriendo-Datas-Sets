"""
Test mejorado: detecta y hace click en botón "Ver teléfono" con clase btn-secondary
Usa el perfil de Chrome del usuario para mantener sesión autenticada
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

# AJUSTA ESTO CON TU RUTA REAL de Chrome User Data
# Por ejemplo: r"C:\Users\Miguel\AppData\Local\Google\Chrome\User Data"
CHROME_USER_DATA = os.environ.get('CHROME_USER_DATA_DIR', None)

if not CHROME_USER_DATA:
    print("⚠️  CHROME_USER_DATA_DIR no está configurada")
    print("Necesitas establecerla con tu ruta de Chrome User Data")
    print("Ejemplo: $env:CHROME_USER_DATA_DIR = 'C:\\Users\\TU_USUARIO\\AppData\\Local\\Google\\Chrome\\User Data'")
    print("\nUsando perfil temporal...")
    CHROME_USER_DATA = tempfile.mkdtemp()
else:
    print(f"✓ Usando Chrome User Data: {CHROME_USER_DATA}")

opts = Options()
opts.add_argument(f"--user-data-dir={CHROME_USER_DATA}")
opts.add_argument("--disable-blink-features=AutomationControlled")
opts.add_experimental_option("excludeSwitches", ["enable-automation"])
opts.add_experimental_option('useAutomationExtension', False)
opts.add_argument("--disable-notifications")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")

try:
    print("\n[1] Iniciando Chrome...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    print("✓ Chrome iniciado\n")
    
    # Ir a la URL
    test_url = "https://www.fincaraiz.com.co/inmobiliarias/perfil/176359705"
    print(f"[2] Abriendo: {test_url}")
    driver.get(test_url)
    time.sleep(3)
    print("✓ Página cargada\n")
    
    wait = WebDriverWait(driver, 10)
    
    # Buscar el botón específico
    print("[3] Buscando botón 'Ver teléfono' con clase 'btn-secondary'...")
    try:
        # Selector XPath para encontrar el botón
        button_xpath = "//button[@class='btn-secondary' and contains(text(), 'Ver teléfono')]"
        print(f"  XPath: {button_xpath}")
        
        button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)), timeout=5)
        print("✓ Botón encontrado!\n")
        
        # Hacer scroll hasta el botón
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(0.5)
        
        # Hacer click
        print("[4] Haciendo click...")
        button.click()
        print("✓ Click realizado\n")
        
        # Esperar a que aparezca el teléfono
        print("[5] Esperando 3 segundos a que se revele el número...")
        time.sleep(3)
        print("✓ Tiempo de espera completado\n")
        
        # Capturar el HTML actualizado
        html = driver.page_source
        body_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Buscar el número
        print("[6] Buscando el número telefónico revelado...")
        print(f"  Primeras 500 caracteres de texto visible:")
        print(f"  {body_text[:500]}...\n")
        
        # Mostrar parte del HTML que contiene el número
        import re
        phone_pattern = r'\+57\s*3[\d\s\-()]{7,}'
        matches = re.findall(phone_pattern, html)
        if matches:
            print(f"✓ Patrones encontrados: {matches[:3]}")
        else:
            print("⚠️  No se encontraron patrones +57 3...")
            # Buscar cualquier número
            alt_pattern = r'3[\d]{9,10}'
            alt_matches = re.findall(alt_pattern, html)
            if alt_matches:
                print(f"  Números encontrados (sin +57): {alt_matches[:3]}")
        
        driver.quit()
        print("\n✓ PRUEBA COMPLETADA")
        
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
        # Mostrar HTML para diagnosticar
        print("\nHTML actual (primeros 1000 chars):")
        print(driver.page_source[:1000])
        driver.quit()

except Exception as e:
    print(f"\n✗ ERROR PRINCIPAL: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
