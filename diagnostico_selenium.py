"""
Script de diagnóstico para Selenium + Chrome remote debugging
Muestra cada paso y qué sale mal (si algo falla)
"""
import os
import sys

print("=" * 60)
print("DIAGNÓSTICO SELENIUM + CHROME")
print("=" * 60)

# Paso 1: Verificar Selenium
print("\n[1] Verificando si selenium está instalado...")
try:
    import selenium
    print(f"✓ Selenium {selenium.__version__} encontrado")
except ImportError as e:
    print(f"✗ Error: selenium no está instalado: {e}")
    sys.exit(1)

# Paso 2: Verificar webdriver_manager
print("\n[2] Verificando si webdriver_manager está instalado...")
try:
    import webdriver_manager
    print(f"✓ webdriver_manager encontrado")
except ImportError as e:
    print(f"✗ Error: webdriver_manager no está instalado: {e}")
    sys.exit(1)

# Paso 3: Verificar puerto
print("\n[3] Verificando puerto de debugging...")
PORT = os.environ.get('CHROME_REMOTE_DEBUGGING_PORT', '9222')
print(f"Puerto configurado: {PORT}")
ADDRESS = f"127.0.0.1:{PORT}"
print(f"Dirección de conexión: {ADDRESS}")

# Paso 4: Intentar conectar
print("\n[4] Intentando conectar a Chrome...")
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    print("  - Creando opciones de Chrome...")
    opts = Options()
    opts.add_experimental_option('debuggerAddress', ADDRESS)
    print(f"  - Debugger address: {ADDRESS}")
    
    print("  - Obteniendo ruta de ChromeDriver...")
    driver_path = ChromeDriverManager().install()
    print(f"  - ChromeDriver en: {driver_path}")
    
    print("  - Iniciando servicio...")
    service = Service(driver_path)
    
    print("  - Creando driver...")
    driver = webdriver.Chrome(service=service, options=opts)
    print(f"✓ CONECTADO a Chrome")
    
    # Paso 5: Obtener info
    print("\n[5] Información de la sesión...")
    print(f"Título actual: {driver.title}")
    print(f"URL actual: {driver.current_url}")
    
    driver.quit()
    print("\n✓ TODO FUNCIONÓ CORRECTAMENTE")
    
except ConnectionRefusedError as e:
    print(f"\n✗ ERROR: No se pudo conectar al puerto {PORT}")
    print("  CAUSAS POSIBLES:")
    print("  1. Chrome NO está abierto con --remote-debugging-port=9222")
    print("  2. El puerto 9222 está bloqueado o en uso por otro proceso")
    print("  3. Chrome se cerró o el puerto no coincide")
    print(f"\n  Comando para abrir Chrome correctamente:")
    print(f"  chrome.exe --remote-debugging-port=9222")
    
except Exception as e:
    print(f"\n✗ ERROR inesperado: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
