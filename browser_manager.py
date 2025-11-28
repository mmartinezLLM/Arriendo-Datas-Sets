"""
Gestor de navegador Selenium
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from config import (
    BROWSER_TYPE, HEADLESS, IMPLICIT_WAIT, PAGE_LOAD_TIMEOUT, 
    USE_PROXY, PROXY_URL, USER_AGENT
)
from config import CHROME_USER_DATA_DIR, CHROME_PROFILE_DIR, CHROME_REMOTE_DEBUGGING_PORT
from logger_config import get_logger

logger = get_logger()

class BrowserManager:
    """Gestor de navegador Selenium"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
    
    def initialize_browser(self):
        """Inicializa el navegador según la configuración"""
        try:
            if BROWSER_TYPE.lower() == "chrome":
                self.driver = self._create_chrome_driver()
            elif BROWSER_TYPE.lower() == "firefox":
                self.driver = self._create_firefox_driver()
            else:
                raise ValueError(f"Navegador no soportado: {BROWSER_TYPE}")
            
            # Configuración de timeouts
            self.driver.implicitly_wait(IMPLICIT_WAIT)
            self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
            
            # Crear wait explícito
            self.wait = WebDriverWait(self.driver, PAGE_LOAD_TIMEOUT)
            
            logger.info(f"Navegador {BROWSER_TYPE} inicializado exitosamente")
            return self.driver
        
        except Exception as e:
            logger.error(f"Error al inicializar el navegador: {str(e)}")
            raise
    
    def _create_chrome_driver(self):
        """Crea un driver de Chrome con opciones configuradas"""
        options = ChromeOptions()
        
        if HEADLESS:
            options.add_argument("--headless")
        # If remote debugging port is set, we'll try to attach to an already-running Chrome
        if CHROME_REMOTE_DEBUGGING_PORT:
            # Connect to a Chrome instance started with: chrome --remote-debugging-port=9222
            logger.info(f"Intentando conectar a Chrome en remote debugging port {CHROME_REMOTE_DEBUGGING_PORT}")
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_REMOTE_DEBUGGING_PORT}")

        # If a user-data-dir is provided, use it so the browser can reuse an existing profile
        if CHROME_USER_DATA_DIR:
            logger.info(f"Usando CHROME_USER_DATA_DIR: {CHROME_USER_DATA_DIR} profile: {CHROME_PROFILE_DIR}")
            options.add_argument(f"--user-data-dir={CHROME_USER_DATA_DIR}")
            if CHROME_PROFILE_DIR:
                options.add_argument(f"--profile-directory={CHROME_PROFILE_DIR}")

        options.add_argument(f"user-agent={USER_AGENT}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        
        if USE_PROXY and PROXY_URL:
            options.add_argument(f"--proxy-server={PROXY_URL}")
        
        try:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            return driver
        except Exception as e:
            logger.error("Error creando Chrome driver: %s", e)
            # Proveer una excepción más informativa para el usuario
            raise RuntimeError(
                "No se pudo iniciar ChromeDriver. Asegúrate de que 'selenium' y 'webdriver-manager' estén instalados en la venv activa, "
                "que la versión del ChromeDriver sea compatible con tu Chrome, y que el path de CHROME_USER_DATA_DIR sea correcto. "
                f"Error original: {e}"
            )
    
    def _create_firefox_driver(self):
        """Crea un driver de Firefox con opciones configuradas"""
        options = FirefoxOptions()
        
        if HEADLESS:
            options.add_argument("--headless")
        
        options.set_preference("general.useragent.override", USER_AGENT)
        
        if USE_PROXY and PROXY_URL:
            options.add_argument(f"--proxy-server={PROXY_URL}")
        
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        return driver
    
    def get_driver(self):
        """Retorna el driver actual"""
        return self.driver
    
    def get_wait(self):
        """Retorna el WebDriverWait actual"""
        return self.wait
    
    def close_browser(self):
        """Cierra el navegador"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Navegador cerrado exitosamente")
            except Exception as e:
                logger.error(f"Error al cerrar navegador: {str(e)}")
