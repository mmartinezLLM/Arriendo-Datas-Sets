"""
Script principal mejorado con adaptador específico para fincaraiz.com.co
"""
import time
import sys
from config import BASE_URL
from logger_config import get_logger
from browser_manager import BrowserManager
from fincaraiz_adapter import FincaraizAdapter
from data_saver import DataSaver

logger = get_logger()

def main():
    """Función principal del scraper mejorado"""
    browser_manager = None
    
    try:
        logger.info("=" * 70)
        logger.info("SCRAPER DE INMOBILIARIAS - FINCARAIZ.COM.CO")
        logger.info("=" * 70)
        logger.info(f"URL objetivo: {BASE_URL}")
        logger.info(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Inicializar navegador
        logger.info("-" * 70)
        logger.info("PASO 1: Inicializando navegador...")
        logger.info("-" * 70)
        
        browser_manager = BrowserManager()
        driver = browser_manager.initialize_browser()
        wait = browser_manager.get_wait()
        
        # Acceder a la URL
        logger.info(f"Accediendo a {BASE_URL}...")
        driver.get(BASE_URL)
        
        # Esperar carga
        logger.info("Esperando carga de página...")
        time.sleep(5)
        
        # Crear adaptador
        logger.info("-" * 70)
        logger.info("PASO 2: Detectando estructura de la página...")
        logger.info("-" * 70)
        
        adapter = FincaraizAdapter(driver, wait)
        adapter.export_detection_report()
        
        # Extraer inmobiliarias
        logger.info("-" * 70)
        logger.info("PASO 3: Extrayendo datos de inmobiliarias...")
        logger.info("-" * 70)
        
        inmobiliarias = adapter.extract_all_inmobiliarias()
        
        if inmobiliarias:
            logger.info("-" * 70)
            logger.info("PASO 4: Guardando datos...")
            logger.info("-" * 70)
            
            # Guardar datos
            saver = DataSaver()
            filepath = saver.save_data(inmobiliarias)
            
            # Mostrar resumen
            summary = saver.get_summary(inmobiliarias)
            
            logger.info("=" * 70)
            logger.info("RESUMEN DE EXTRACCIÓN")
            logger.info("=" * 70)
            for key, value in summary.items():
                logger.info(f"  {key}: {value}")
            logger.info("=" * 70)
            
            # Mostrar algunas muestras
            logger.info("\nMUESTRAS DE DATOS EXTRAÍDOS:")
            logger.info("-" * 70)
            for idx, inmobiliaria in enumerate(inmobiliarias[:3], 1):
                logger.info(f"\nInmobiliaria #{idx}:")
                logger.info(f"  Título: {inmobiliaria.get('titulo')}")
                logger.info(f"  Correo: {inmobiliaria.get('correo')}")
                logger.info(f"  Teléfono: {inmobiliaria.get('telefono')}")
                logger.info(f"  Inmuebles: {inmobiliaria.get('cantidad_inmuebles')}")
            logger.info("=" * 70)
            
            logger.info(f"\nDatos completos guardados en: {filepath}")
        else:
            logger.warning("No se extrajeron datos. Revisa los logs para más información.")
            logger.warning("Sugerencias:")
            logger.warning("1. Verifica que fincaraiz.com.co esté disponible")
            logger.warning("2. Revisa el archivo 'detection_report.json' en la carpeta resultados/")
            logger.warning("3. Puede que la estructura HTML haya cambiado")
            logger.warning("4. Intenta con HEADLESS=False en config.py para ver la página")
        
        logger.info("-" * 70)
        logger.info("SCRAPER COMPLETADO")
        logger.info("=" * 70)
    
    except KeyboardInterrupt:
        logger.info("\nScraper interrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error general en el scraper: {str(e)}", exc_info=True)
    
    finally:
        # Cerrar navegador
        if browser_manager:
            logger.info("Cerrando navegador...")
            browser_manager.close_browser()
        
        logger.info("Script finalizado")

if __name__ == "__main__":
    main()
