"""
Extractor avanzado con manejo de interacciones complejas
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located, element_to_be_clickable
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup
import time
import re
from config import WAIT_TIME, MAX_RETRIES, SCROLL_PAUSE_TIME
from logger_config import get_logger

logger = get_logger()

class AdvancedInmobiliariaExtractor:
    """Extractor avanzado de información de inmobiliarias con soporte para interacciones"""
    
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        self.actions = ActionChains(driver)
        self.inmobiliarias = []
    
    def extract_with_interactions(self, elemento_web, selectors):
        """
        Extrae datos realizando interacciones cuando sea necesario
        
        Args:
            elemento_web: Elemento web de Selenium
            selectors: Diccionario con selectores de elementos
        """
        datos = {}
        
        try:
            # Scroll al elemento
            self.driver.execute_script("arguments[0].scrollIntoView(true);", elemento_web)
            time.sleep(0.5)
            
            # Extraer título
            datos['titulo'] = self._safe_extract(elemento_web, selectors.get('titulo_selector'))
            
            # Extraer correo
            datos['correo'] = self._safe_extract(elemento_web, selectors.get('correo_selector'))
            
            # Extraer teléfono (puede requerir interacción)
            datos['telefono'] = self._extract_phone_with_click(
                elemento_web, 
                selectors.get('telefono_selector'),
                selectors.get('phone_button_selector')
            )
            
            # Extraer cantidad de inmuebles
            datos['cantidad_inmuebles'] = self._extract_number(
                elemento_web,
                selectors.get('cantidad_selector')
            )
            
            # Extraer URL
            datos['url'] = self._extract_url_safe(elemento_web, selectors.get('url_selector'))
            
            return datos
        
        except Exception as e:
            logger.error(f"Error extrayendo con interacciones: {str(e)}")
            return None
    
    def _safe_extract(self, elemento, selector, attribute=None):
        """Extrae texto de forma segura"""
        try:
            if not selector:
                return "No disponible"
            
            if isinstance(selector, dict):
                by, value = self._parse_selector(selector)
            else:
                return "No disponible"
            
            element = elemento.find_element(by, value)
            
            if attribute:
                return element.get_attribute(attribute) or "No disponible"
            else:
                return element.text.strip() or "No disponible"
        
        except (NoSuchElementException, StaleElementReferenceException):
            return "No disponible"
        except Exception as e:
            logger.debug(f"Error en extracción segura: {str(e)}")
            return "Error en extracción"
    
    def _extract_phone_with_click(self, elemento, phone_selector, button_selector=None):
        """Extrae teléfono intentando hacer clic si es necesario"""
        try:
            # Primero intentar obtener el teléfono visible
            if phone_selector:
                telefono = self._safe_extract(elemento, phone_selector)
                if telefono and telefono not in ["No disponible", "Error en extracción"]:
                    return telefono
            
            # Si no está visible y hay un botón, intentar clickearlo
            if button_selector:
                try:
                    by, value = self._parse_selector(button_selector)
                    button = elemento.find_element(by, value)
                    
                    # Scroll al botón
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(0.3)
                    
                    # Hacer clic
                    self.actions.move_to_element(button).click().perform()
                    time.sleep(1)
                    
                    # Intentar nuevo extracción
                    if phone_selector:
                        telefono = self._safe_extract(elemento, phone_selector)
                        if telefono and telefono not in ["No disponible", "Error en extracción"]:
                            return telefono
                    
                except (NoSuchElementException, StaleElementReferenceException):
                    pass
            
            return "Requiere inicio de sesión"
        
        except Exception as e:
            logger.debug(f"Error extrayendo teléfono: {str(e)}")
            return "Requiere inicio de sesión"
    
    def _extract_number(self, elemento, selector):
        """Extrae número de cantidad"""
        try:
            if not selector:
                return 0
            
            text = self._safe_extract(elemento, selector)
            if text and text not in ["No disponible", "Error en extracción"]:
                # Buscar todos los números en el texto
                numbers = re.findall(r'\d+', text)
                return int(numbers[0]) if numbers else 0
            
            return 0
        
        except Exception as e:
            logger.debug(f"Error extrayendo número: {str(e)}")
            return 0
    
    def _extract_url_safe(self, elemento, selector):
        """Extrae URL de forma segura"""
        try:
            if not selector:
                return "No disponible"
            
            if isinstance(selector, dict):
                by, value = self._parse_selector(selector)
            else:
                return "No disponible"
            
            element = elemento.find_element(by, value)
            href = element.get_attribute("href")
            
            if href:
                # Convertir a URL absoluta si es relativa
                if href.startswith('http'):
                    return href
                elif href.startswith('/'):
                    return "https://www.fincaraiz.com.co" + href
                else:
                    return "https://www.fincaraiz.com.co/" + href
            
            return "No disponible"
        
        except (NoSuchElementException, StaleElementReferenceException):
            return "No disponible"
        except Exception as e:
            logger.debug(f"Error extrayendo URL: {str(e)}")
            return "No disponible"
    
    def _parse_selector(self, selector_dict):
        """Parsea un selector a formato Selenium"""
        method = selector_dict.get('method', 'css')
        value = selector_dict.get('value')
        
        if method == 'xpath':
            return By.XPATH, value
        elif method == 'class':
            return By.CLASS_NAME, value
        elif method == 'id':
            return By.ID, value
        elif method == 'tag':
            return By.TAG_NAME, value
        else:  # css por defecto
            return By.CSS_SELECTOR, value
    
    def get_all_with_interactions(self, lista_elementos, selectors_map):
        """
        Obtiene todas las inmobiliarias con interacciones
        
        Args:
            lista_elementos: Lista de elementos web de Selenium
            selectors_map: Diccionario con mapeo de selectores
        """
        for idx, elemento in enumerate(lista_elementos, 1):
            try:
                datos = self.extract_with_interactions(elemento, selectors_map)
                if datos:
                    self.inmobiliarias.append(datos)
                    logger.info(f"[{idx}/{len(lista_elementos)}] Extraído: {datos.get('titulo', 'Sin nombre')}")
            
            except Exception as e:
                logger.warning(f"Error procesando elemento {idx}: {str(e)}")
                continue
        
        logger.info(f"Total de inmobiliarias extraídas: {len(self.inmobiliarias)}")
        return self.inmobiliarias
    
    def wait_for_elements(self, locator, timeout=WAIT_TIME):
        """Espera a que aparezcan elementos"""
        try:
            by, value = self._parse_selector(locator) if isinstance(locator, dict) else (By.CSS_SELECTOR, locator)
            elements = self.wait.until(presence_of_all_elements_located((by, value)))
            return elements
        except TimeoutException:
            logger.warning(f"Timeout esperando elementos: {locator}")
            return []
