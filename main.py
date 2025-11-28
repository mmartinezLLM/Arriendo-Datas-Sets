"""
Script principal para ejecutar el scraper de inmobiliarias
"""
import time
from config import BASE_URL
from logger_config import get_logger
from browser_manager import BrowserManager
from extractor import InmobiliariaExtractor
from data_saver import DataSaver

logger = get_logger()

def main():
    """Función principal del scraper"""
    browser_manager = None
    
    try:
        logger.info("=" * 60)
        logger.info("INICIANDO SCRAPER DE INMOBILIARIAS")
        logger.info("=" * 60)
        logger.info(f"URL objetivo: {BASE_URL}")
        
        # Inicializar navegador
        browser_manager = BrowserManager()
        driver = browser_manager.initialize_browser()
        wait = browser_manager.get_wait()
        
        # Acceder a la URL
        logger.info(f"Accediendo a {BASE_URL}...")
        driver.get(BASE_URL)
        
        # Esperar un poco para que cargue la página
        time.sleep(3)
        
        # Crear extractor
        extractor = InmobiliariaExtractor(driver, wait)
        
        # Extraer todas las inmobiliarias
        inmobiliarias = extractor.get_all_inmobiliarias()
        
        if inmobiliarias:
            # Guardar datos
            saver = DataSaver()
            filepath = saver.save_data(inmobiliarias)
            
            # Mostrar resumen
            summary = saver.get_summary(inmobiliarias)
            logger.info("=" * 60)
            logger.info("RESUMEN DE EXTRACCIÓN")
            logger.info("=" * 60)
            for key, value in summary.items():
                logger.info(f"{key}: {value}")
            logger.info("=" * 60)
        else:
            logger.warning("No se extrajeron datos")
        
        logger.info("SCRAPER COMPLETADO")
    
    except Exception as e:
        logger.error(f"Error general en el scraper: {str(e)}", exc_info=True)
    
    finally:
        # Cerrar navegador
        if browser_manager:
            browser_manager.close_browser()
        
        logger.info("Script finalizado")

if __name__ == "__main__":
    main()
