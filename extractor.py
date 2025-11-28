"""
Extractor de datos de inmobiliarias
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located, element_to_be_clickable
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup
import time
from config import WAIT_TIME, MAX_RETRIES, SCROLL_PAUSE_TIME
from logger_config import get_logger

logger = get_logger()

class InmobiliariaExtractor:
    """Extractor de información de inmobiliarias"""
    
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        self.inmobiliarias = []
    
    def scrape_inmobiliarias_list(self):
        """Obtiene la lista de inmobiliarias de la página principal"""
        try:
            logger.info("Iniciando extracción de lista de inmobiliarias...")
            
            # Esperar a que carguen los elementos de inmobiliarias
            self.wait.until(presence_of_all_elements_located((By.CLASS_NAME, "inmobiliaria-item")))
            
            # Hacer scroll para cargar más inmobiliarias
            self._scroll_to_load_all()
            
            # Obtener el HTML de la página
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Buscar todos los elementos de inmobiliarias
            inmobiliaria_elements = soup.find_all('div', {'class': 'inmobiliaria-item'})
            
            logger.info(f"Se encontraron {len(inmobiliaria_elements)} inmobiliarias")
            
            return inmobiliaria_elements
        
        except TimeoutException:
            logger.error("Timeout esperando por elementos de inmobiliarias")
            return []
        except Exception as e:
            logger.error(f"Error al obtener lista de inmobiliarias: {str(e)}")
            return []
    
    def extract_inmobiliaria_data(self, elemento):
        """Extrae datos de una inmobiliaria específica"""
        try:
            datos = {
                'titulo': self._extract_titulo(elemento),
                'correo': self._extract_correo(elemento),
                'telefono': self._extract_telefono(elemento),
                'cantidad_inmuebles': self._extract_cantidad_inmuebles(elemento),
                'url': self._extract_url(elemento)
            }
            return datos
        
        except Exception as e:
            logger.error(f"Error al extraer datos de inmobiliaria: {str(e)}")
            return None
    
    def _extract_titulo(self, elemento):
        """Extrae el título de la inmobiliaria"""
        try:
            titulo = elemento.find('h2', {'class': 'inmobiliaria-nombre'})
            if titulo:
                return titulo.get_text(strip=True)
            return "No especificado"
        except Exception as e:
            logger.warning(f"Error extrayendo título: {str(e)}")
            return "Error en extracción"
    
    def _extract_correo(self, elemento):
        """Extrae el correo de la inmobiliaria"""
        try:
            # Buscar en el elemento o en un atributo data
            correo_element = elemento.find('a', {'class': 'email-link'})
            if correo_element:
                return correo_element.get_text(strip=True)
            
            # Intenta buscar en atributos de datos
            correo = elemento.get('data-email', '')
            return correo if correo else "No disponible"
        
        except Exception as e:
            logger.warning(f"Error extrayendo correo: {str(e)}")
            return "Error en extracción"
    
    def _extract_telefono(self, elemento):
        """Extrae el teléfono de la inmobiliaria"""
        try:
            # El teléfono puede estar oculto y requerir clic
            # Intentar encontrarlo en atributos de datos primero
            telefono = elemento.get('data-phone', '')
            if telefono:
                return telefono
            
            # Buscar en elementos visibles
            phone_element = elemento.find('span', {'class': 'telefono'})
            if phone_element:
                return phone_element.get_text(strip=True)
            
            return "Requiere inicio de sesión"
        
        except Exception as e:
            logger.warning(f"Error extrayendo teléfono: {str(e)}")
            return "Error en extracción"
    
    def _extract_cantidad_inmuebles(self, elemento):
        """Extrae la cantidad de inmuebles de la inmobiliaria"""
        try:
            count_element = elemento.find('span', {'class': 'count-inmuebles'})
            if count_element:
                text = count_element.get_text(strip=True)
                # Extraer número de texto como "234 inmuebles"
                numero = ''.join(filter(str.isdigit, text.split()[0])) if text else "0"
                return int(numero) if numero else 0
            return 0
        
        except Exception as e:
            logger.warning(f"Error extrayendo cantidad de inmuebles: {str(e)}")
            return 0
    
    def _extract_url(self, elemento):
        """Extrae la URL de la inmobiliaria"""
        try:
            link = elemento.find('a', {'class': 'inmobiliaria-link'})
            if link:
                href = link.get('href', '')
                # Asegurar que es una URL completa
                if href.startswith('http'):
                    return href
                elif href.startswith('/'):
                    return "https://www.fincaraiz.com.co" + href
            return "No disponible"
        
        except Exception as e:
            logger.warning(f"Error extrayendo URL: {str(e)}")
            return "Error en extracción"
    
    def _scroll_to_load_all(self, max_scrolls=10):
        """Hace scroll para cargar todas las inmobiliarias"""
        try:
            logger.info("Realizando scrolls para cargar todas las inmobiliarias...")
            
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scrolls = 0
            
            while scrolls < max_scrolls:
                # Scroll hacia abajo
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # Esperar carga
                time.sleep(SCROLL_PAUSE_TIME)
                
                # Calcular nueva altura
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    logger.info("Se alcanzó el final de la página")
                    break
                
                last_height = new_height
                scrolls += 1
                logger.info(f"Scroll {scrolls}/{max_scrolls} completado")
        
        except Exception as e:
            logger.warning(f"Error durante scroll: {str(e)}")
    
    def click_phone_button_if_needed(self, elemento_web):
        """Intenta hacer clic en el botón de teléfono si es necesario"""
        try:
            # Buscar botón que revela el teléfono
            phone_button = elemento_web.find_element(By.CLASS_NAME, "reveal-phone")
            if phone_button:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", phone_button)
                time.sleep(0.5)
                self.wait.until(element_to_be_clickable((By.CLASS_NAME, "reveal-phone")))
                phone_button.click()
                time.sleep(1)
                logger.info("Botón de teléfono clickeado")
                return True
        except (NoSuchElementException, StaleElementReferenceException, TimeoutException):
            pass
        
        return False
    
    def get_all_inmobiliarias(self):
        """Obtiene todas las inmobiliarias con sus datos"""
        try:
            elementos = self.scrape_inmobiliarias_list()
            
            for idx, elemento in enumerate(elementos, 1):
                try:
                    # Convertir a elemento web de Selenium
                    elemento_html = str(elemento)
                    
                    # Extraer datos
                    datos = self.extract_inmobiliaria_data(elemento)
                    
                    if datos:
                        self.inmobiliarias.append(datos)
                        logger.info(f"[{idx}/{len(elementos)}] Inmobiliaria extraída: {datos['titulo']}")
                
                except Exception as e:
                    logger.warning(f"Error procesando elemento {idx}: {str(e)}")
                    continue
            
            logger.info(f"Total de inmobiliarias extraídas: {len(self.inmobiliarias)}")
            return self.inmobiliarias
        
        except Exception as e:
            logger.error(f"Error obteniendo todas las inmobiliarias: {str(e)}")
            return []
