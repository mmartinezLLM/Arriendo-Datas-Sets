"""
Script de utilidad para inspeccionar y configurar selectores
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import json
import time
from config import BASE_URL, WAIT_TIME, OUTPUT_DIR
from logger_config import get_logger
from browser_manager import BrowserManager
import os

logger = get_logger()

class SelectorInspector:
    """Herramienta para inspeccionar y configurar selectores"""
    
    def __init__(self, driver):
        self.driver = driver
        self.elements_found = {}
    
    def inspect_page(self):
        """Inspecciona la página y obtiene información detallada"""
        logger.info("Iniciando inspección de página...")
        
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        inspection_data = {
            'title': self.driver.title,
            'url': self.driver.current_url,
            'all_classes': set(),
            'all_ids': set(),
            'all_data_attributes': set(),
            'divs_with_class': {},
            'articles': soup.find_all('article'),
            'elements_by_pattern': {}
        }
        
        # Recopilar todas las clases
        for element in soup.find_all(class_=True):
            classes = element.get('class', [])
            for cls in classes:
                inspection_data['all_classes'].add(cls)
        
        # Recopilar todos los IDs
        for element in soup.find_all(id=True):
            inspection_data['all_ids'].add(element.get('id'))
        
        # Recopilar atributos data-*
        for element in soup.find_all():
            for attr in element.attrs:
                if attr.startswith('data-'):
                    inspection_data['all_data_attributes'].add(attr)
        
        # Buscar divs y articles con palabras clave
        keywords = ['company', 'inmobiliaria', 'card', 'item', 'listing', 'property', 'real']
        
        for keyword in keywords:
            matches = soup.find_all(['div', 'article', 'section', 'li'], 
                                  class_=lambda x: x and keyword.lower() in str(x).lower())
            if matches:
                inspection_data['elements_by_pattern'][keyword] = {
                    'count': len(matches),
                    'sample_classes': [m.get('class', []) for m in matches[:3]]
                }
        
        # Convertir sets a listas para JSON
        inspection_data['all_classes'] = list(inspection_data['all_classes'])
        inspection_data['all_ids'] = list(inspection_data['all_ids'])
        inspection_data['all_data_attributes'] = list(inspection_data['all_data_attributes'])
        
        return inspection_data
    
    def save_inspection_report(self, inspection_data):
        """Guarda el reporte de inspección"""
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        filepath = os.path.join(OUTPUT_DIR, 'inspection_report.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(inspection_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Reporte de inspección guardado en: {filepath}")
        return filepath
    
    def print_inspection_summary(self, inspection_data):
        """Imprime un resumen de la inspección"""
        logger.info("\n" + "=" * 70)
        logger.info("RESUMEN DE INSPECCIÓN DE PÁGINA")
        logger.info("=" * 70)
        logger.info(f"Título: {inspection_data.get('title')}")
        logger.info(f"URL: {inspection_data.get('url')}")
        logger.info(f"\nClases encontradas: {len(inspection_data.get('all_classes', []))}")
        logger.info(f"IDs encontrados: {len(inspection_data.get('all_ids', []))}")
        logger.info(f"Atributos data-*: {len(inspection_data.get('all_data_attributes', []))}")
        
        logger.info("\nClases relevantes (muestra):")
        relevant_classes = [c for c in inspection_data.get('all_classes', []) 
                           if any(keyword in c.lower() for keyword in 
                           ['company', 'inmobiliaria', 'card', 'item', 'property'])]
        for cls in relevant_classes[:10]:
            logger.info(f"  .{cls}")
        
        logger.info("\nElementos por patrón:")
        for keyword, data in inspection_data.get('elements_by_pattern', {}).items():
            logger.info(f"  {keyword}: {data.get('count')} elementos")
        
        logger.info("=" * 70 + "\n")

def main():
    """Script principal de inspección"""
    browser_manager = None
    
    try:
        logger.info("HERRAMIENTA DE INSPECCIÓN DE SELECTORES")
        logger.info("=" * 70)
        
        # Inicializar navegador
        browser_manager = BrowserManager()
        driver = browser_manager.initialize_browser()
        
        logger.info(f"Accediendo a {BASE_URL}...")
        driver.get(BASE_URL)
        
        logger.info("Esperando carga de página...")
        time.sleep(5)
        
        # Inspeccionar
        inspector = SelectorInspector(driver)
        inspection_data = inspector.inspect_page()
        
        # Guardar y mostrar
        inspector.save_inspection_report(inspection_data)
        inspector.print_inspection_summary(inspection_data)
        
        logger.info("Inspección completada. Revisa 'resultados/inspection_report.json' para detalles.")
    
    except Exception as e:
        logger.error(f"Error en inspección: {str(e)}", exc_info=True)
    
    finally:
        if browser_manager:
            browser_manager.close_browser()

if __name__ == "__main__":
    main()
