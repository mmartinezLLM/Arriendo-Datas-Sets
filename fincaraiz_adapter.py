"""
Adaptador específico para fincaraiz.com.co
Detecta e inspecciona la estructura real de la página
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import json
from config import BASE_URL, WAIT_TIME
from logger_config import get_logger
from advanced_extractor import AdvancedInmobiliariaExtractor

logger = get_logger()

class FincaraizAdapter:
    """Adaptador especializado para fincaraiz.com.co"""
    
    # Selectores detectados para fincaraiz.com.co
    SELECTORS = {
        # Contenedor de inmobiliarias
        'container': {
            'method': 'css',
            'value': '[data-testid="companyCardWrapper"], .company-card, .inmobiliaria-card'
        },
        
        # Título/Nombre
        'titulo': {
            'method': 'css',
            'value': 'h2, .company-name, [data-testid="companyName"], .inmobiliaria-nombre'
        },
        
        # Correo
        'correo': {
            'method': 'css',
            'value': 'a[href^="mailto:"], .company-email, [data-testid="email"], .email-link'
        },
        
        # Teléfono (botón para revelar)
        'phone_button': {
            'method': 'xpath',
            'value': '//button[contains(text(), "Mostrar")], //button[contains(text(), "Ver"), contains(text(), "teléfono")]'
        },
        
        # Teléfono (el número)
        'telefono': {
            'method': 'css',
            'value': '.company-phone, [data-testid="phone"], .telefono, a[href^="tel:"]'
        },
        
        # Cantidad de inmuebles
        'cantidad': {
            'method': 'css',
            'value': '.property-count, [data-testid="propertyCount"], .inmuebles-count'
        },
        
        # URL/Link
        'url': {
            'method': 'css',
            'value': 'a[href], [data-testid="companyLink"]'
        }
    }
    
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        self.extractor = AdvancedInmobiliariaExtractor(driver, wait)
    
    def detect_structure(self):
        """Detecta la estructura real de la página"""
        logger.info("Detectando estructura de la página...")
        
        try:
            # Obtener HTML
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Intentar encontrar contenedores
            detection_report = {
                'url': self.driver.current_url,
                'page_title': self.driver.title,
                'containers_found': 0,
                'container_classes': [],
                'container_ids': [],
                'data_attributes': []
            }
            
            # Buscar posibles contenedores
            possible_containers = soup.find_all(['div', 'article', 'li', 'section'])
            
            for container in possible_containers:
                if any(keyword in str(container.get('class', [])).lower() for keyword in 
                       ['company', 'inmobiliaria', 'card', 'item', 'listing']):
                    detection_report['containers_found'] += 1
                    if container.get('class'):
                        detection_report['container_classes'].extend(container.get('class', []))
                    if container.get('id'):
                        detection_report['container_ids'].append(container.get('id'))
                    if container.get('data-testid'):
                        detection_report['data_attributes'].append(container.get('data-testid'))
            
            logger.info(f"Reporte de detección: {json.dumps(detection_report, indent=2)}")
            return detection_report
        
        except Exception as e:
            logger.error(f"Error detectando estructura: {str(e)}")
            return None
    
    def find_inmobiliarias_elements(self):
        """Encuentra elementos de inmobiliarias usando múltiples estrategias"""
        logger.info("Buscando elementos de inmobiliarias...")
        
        elementos = []
        
        # Estrategia 1: Usando el selector configurado
        try:
            elementos = self.wait.until(presence_of_all_elements_located(
                (By.CSS_SELECTOR, self.SELECTORS['container']['value'])
            ))
            logger.info(f"Se encontraron {len(elementos)} elementos usando CSS selector")
            return elementos
        except TimeoutException:
            logger.warning("Timeout con CSS selector principal, intentando alternativas...")
        
        # Estrategia 2: Intentar con XPath
        try:
            elementos = self.driver.find_elements(By.XPATH, 
                '//div[@class]*="company" | //article | //section[@data-testid]'
            )
            logger.info(f"Se encontraron {len(elementos)} elementos usando XPath")
            return elementos
        except:
            logger.warning("XPath alternativo no funcionó")
        
        # Estrategia 3: Inspeccionar manualmente el HTML
        try:
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Buscar por patrones comunes
            posibles_elementos = soup.find_all(
                ['div', 'article'],
                class_=lambda x: x and any(keyword in x.lower() for keyword in 
                    ['company', 'inmobiliaria', 'card', 'card-', 'listing'])
            )
            
            logger.info(f"Se encontraron {len(posibles_elementos)} elementos por análisis HTML")
            return posibles_elementos
        
        except Exception as e:
            logger.error(f"Error encontrando elementos: {str(e)}")
        
        return []
    
    def extract_all_inmobiliarias(self):
        """Extrae todas las inmobiliarias de la página"""
        logger.info("Iniciando extracción de inmobiliarias...")
        
        try:
            # Detectar estructura
            self.detect_structure()
            
            # Esperar carga de página
            time.sleep(2)
            
            # Buscar elementos
            elementos = self.find_inmobiliarias_elements()
            
            if not elementos:
                logger.warning("No se encontraron elementos de inmobiliarias")
                return []
            
            logger.info(f"Procesando {len(elementos)} inmobiliarias encontradas...")
            
            # Extraer datos de cada elemento
            inmobiliarias = []
            for idx, elemento in enumerate(elementos, 1):
                try:
                    # Scroll al elemento
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
                    time.sleep(0.5)
                    
                    datos = self.extractor.extract_with_interactions(elemento, self.SELECTORS)
                    
                    if datos and any(datos.values()):  # Si hay al menos algún dato
                        inmobiliarias.append(datos)
                        logger.info(f"[{idx}/{len(elementos)}] Extraído: {datos.get('titulo', 'Sin nombre')}")
                    else:
                        logger.debug(f"Elemento {idx} no contiene datos relevantes")
                
                except Exception as e:
                    logger.warning(f"Error procesando elemento {idx}: {str(e)}")
                    continue
            
            logger.info(f"Total de inmobiliarias extraídas exitosamente: {len(inmobiliarias)}")
            return inmobiliarias
        
        except Exception as e:
            logger.error(f"Error en extracción general: {str(e)}", exc_info=True)
            return []
    
    def update_selectors(self, new_selectors):
        """Actualiza los selectores para adaptarse a cambios en la página"""
        logger.info("Actualizando selectores...")
        self.SELECTORS.update(new_selectors)
        logger.info("Selectores actualizados exitosamente")
    
    def export_detection_report(self):
        """Exporta un reporte de detección para debugging"""
        report = self.detect_structure()
        
        # Guardar en archivo
        import os
        from config import OUTPUT_DIR
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        filepath = os.path.join(OUTPUT_DIR, 'detection_report.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Reporte de detección guardado en: {filepath}")
        return filepath
