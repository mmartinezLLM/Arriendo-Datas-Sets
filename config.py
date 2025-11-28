"""
Configuración del scraper de inmobiliarias
"""
import os
from dotenv import load_dotenv

load_dotenv()

# URLs
BASE_URL = "https://www.fincaraiz.com.co/inmobiliarias/"

# Configuración de Selenium
BROWSER_TYPE = "chrome"  # 'chrome' o 'firefox'
HEADLESS = False  # Cambiar a True para ejecutar sin interfaz gráfica
IMPLICIT_WAIT = 10
PAGE_LOAD_TIMEOUT = 30

# Configuración de extracción de datos
SCROLL_PAUSE_TIME = 2  # Tiempo de pausa entre scrolls (segundos)
MAX_RETRIES = 3  # Reintentos para elementos no encontrados
WAIT_TIME = 10  # Tiempo de espera para elementos (segundos)

# Configuración de salida
OUTPUT_DIR = "resultados"
OUTPUT_FORMAT = "csv"  # 'csv', 'json' o 'excel'
LOG_FILE = f"{OUTPUT_DIR}/scraper.log"

# Configuración de proxy (opcional)
USE_PROXY = False
PROXY_URL = os.getenv("PROXY_URL", "")

# User Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Opciones para reutilizar una sesión de Chrome ya existente (útil para acceder a datos que requieren login)
# Ruta al folder "User Data" de Chrome (ej: C:\\Users\\Miguel\\AppData\\Local\\Google\\Chrome\\User Data)
CHROME_USER_DATA_DIR = os.getenv('CHROME_USER_DATA_DIR', '')
# Nombre del profile dentro del user data (por ejemplo: 'Default' o 'Profile 1')
CHROME_PROFILE_DIR = os.getenv('CHROME_PROFILE_DIR', '')
# Puerto para conectar por remote debugging si prefieres iniciar Chrome con --remote-debugging-port
CHROME_REMOTE_DEBUGGING_PORT = os.getenv('CHROME_REMOTE_DEBUGGING_PORT', '')
