"""Prueba: conectar a Chrome ya abierto con --remote-debugging-port
Uso:
1) Abre Chrome con:
   chrome.exe --remote-debugging-port=9222
2) En PowerShell (en la carpeta del proyecto):
   & ".\.venv\Scripts\Activate.ps1"
   $env:CHROME_REMOTE_DEBUGGING_PORT = "9222"
   python scraper_inmobiliarias\selenium_connect_test.py

El script intentará conectarse al puerto indicado y mostrar el título y una URL de prueba.
"""
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

PORT = os.environ.get('CHROME_REMOTE_DEBUGGING_PORT', '9222')
ADDRESS = f"127.0.0.1:{PORT}"

print(f"Intentando conectar a Chrome en {ADDRESS} ...")
opts = Options()
opts.add_experimental_option('debuggerAddress', ADDRESS)

# No headless: estamos conectando a una instancia real
try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    print('Conectado. Título de la ventana:', driver.title)
    test_url = 'https://www.fincaraiz.com.co/inmobiliarias/perfil/176359705'
    print('Abriendo URL de prueba:', test_url)
    driver.get(test_url)
    time.sleep(2)
    print('URL actual:', driver.current_url)
    # intentar localizar un posible selector de teléfono (ejemplo genérico)
    try:
        phone_el = driver.find_element('xpath', "//a[contains(@href, 'tel:') or contains(@href, 'telefono')]")
        print('Encontrado enlace telefonico:', phone_el.get_attribute('href'))
    except Exception:
        print('No se encontró un enlace tel: con el selector simple.')
    driver.quit()
except Exception as e:
    print('ERROR al conectar con ChromeDriver/Chrome:', e)
    print('Asegúrate de haber lanzado Chrome con --remote-debugging-port y de que el puerto coincide.')
