"""
property_crawler_robust.py - Crawler robusto para grandes volúmenes (300k+ inmuebles)

Características:
- Checkpoints incrementales (reanudar sin repetir trabajo)
- Reintentos automáticos con backoff exponencial
- Paralelización controlada (ThreadPool)
- Validación de datos y detección de duplicados
- Logging detallado con métricas de progreso
- Gestión eficiente de memoria en batches
"""
import re
import json
import time
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import hashlib

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


# Configuración global
CONFIG = {
    'checkpoint_interval': 10,  # Guardar cada N URLs
    'max_retries': 3,  # Reintentos por URL
    'retry_delay_base': 2,  # Segundos base para backoff exponencial
    'batch_size': 100,  # Procesar en lotes de N URLs
    'max_workers': 3,  # Threads concurrentes (ajustar según CPU/RAM)
    'request_delay': 0.5,  # Pausa entre requests (segundos)
    'headless': True,
    'page_timeout': 20,  # Timeout por página (segundos)
}


class RobustPropertyCrawler:
    """Crawler optimizado para volúmenes masivos con resiliencia"""
    
    def __init__(self, output_dir: str = 'resultados', config: Dict = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.config = {**CONFIG, **(config or {})}
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Archivos de sesión
        self.checkpoint_file = self.output_dir / f'checkpoint_{self.session_id}.json'
        self.data_file = self.output_dir / f'properties_{self.session_id}.jsonl'
        self.error_file = self.output_dir / f'errors_{self.session_id}.jsonl'
        self.log_file = self.output_dir / f'crawler_{self.session_id}.log'
        
        # Estado interno
        self.processed_urls: Set[str] = set()
        self.failed_urls: Dict[str, int] = {}
        self.lock = Lock()
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': None,
        }
        
        # Configurar logging
        self._setup_logging()
        
        # Cargar checkpoint si existe
        self._load_checkpoint()
    
    def _setup_logging(self):
        """Configura sistema de logging robusto"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_checkpoint(self):
        """Carga checkpoint previo para reanudar"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint = json.load(f)
                self.processed_urls = set(checkpoint.get('processed_urls', []))
                self.failed_urls = checkpoint.get('failed_urls', {})
                self.stats.update(checkpoint.get('stats', {}))
                self.logger.info(f"Checkpoint cargado: {len(self.processed_urls)} URLs ya procesadas")
            except Exception as e:
                self.logger.warning(f"No se pudo cargar checkpoint: {e}")
    
    def _save_checkpoint(self):
        """Guarda checkpoint actual"""
        checkpoint = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'processed_urls': list(self.processed_urls),
            'failed_urls': self.failed_urls,
            'stats': self.stats,
        }
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, ensure_ascii=False, indent=2)
    
    def _append_result(self, data: Dict[str, Any], is_error: bool = False):
        """Guarda resultado en JSONL (append-only para evitar corrupción)"""
        target_file = self.error_file if is_error else self.data_file
        with self.lock:
            with open(target_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    def _create_driver(self):
        """Crea instancia de Selenium WebDriver"""
        chrome_options = Options()
        
        if self.config['headless']:
            chrome_options.add_argument('--headless=new')
        
        # Optimizaciones para rendimiento
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # Desactivar recursos pesados
        prefs = {
            'profile.default_content_setting_values.images': 2,
            'profile.managed_default_content_settings.stylesheets': 2,
            'profile.default_content_setting_values.cookies': 2,
            'profile.default_content_setting_values.plugins': 2,
            'profile.default_content_setting_values.popups': 2,
            'profile.default_content_setting_values.geolocation': 2,
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_setting_values.media_stream': 2,
        }
        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(self.config['page_timeout'])
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _extract_property_data(self, driver, url: str) -> Optional[Dict[str, Any]]:
        """Extrae datos de una propiedad usando el driver"""
        try:
            driver.get(url)
            
            # Esperar __NEXT_DATA__
            wait = WebDriverWait(driver, self.config['page_timeout'])
            wait.until(EC.presence_of_element_located((By.ID, '__NEXT_DATA__')))
            time.sleep(0.5)
            
            html = driver.page_source
            
            # Extraer JSON
            match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.+?)</script>', html, re.DOTALL)
            if not match:
                raise ValueError("__NEXT_DATA__ no encontrado")
            
            json_data = json.loads(match.group(1))
            page_props = json_data.get('props', {}).get('pageProps', {})
            data = page_props.get('data', {})
            technical_sheet = page_props.get('technicalSheet', {})
            
            if not data:
                raise ValueError("No hay datos de propiedad")
            
            # Extraer campos (reutilizar lógica anterior)
            resultado = self._parse_property_data(url, data, technical_sheet, html)
            return resultado
            
        except TimeoutException:
            raise Exception("Timeout cargando página")
        except Exception as e:
            raise Exception(f"Error extrayendo datos: {str(e)}")
    
    def _parse_property_data(self, url: str, data: Dict, technical_sheet: Any, html: str) -> Dict[str, Any]:
        """Parsea datos extraídos y genera estructura final"""
        # Importar helpers de formateo
        from property_crawler_selenium import (
            _si_no_normalizado,
            _inferir_tipo_oferta,
            _formatear_salida_final,
        )
        
        # Estructura intermedia
        raw_data = {
            'url': url,
            'codigo_fr': str(data.get('id')) if data.get('id') else None,
            'codigo_fr_legacy': data.get('code'),
            'h1': data.get('title'),
            'descripcion': data.get('description'),
            'ubicacion': self._extraer_ubicacion(data),
            'habitaciones': self._extraer_habitaciones(technical_sheet),
            'banos': self._extraer_banos(technical_sheet),
            'metros': self._extraer_metros(technical_sheet),
            'precio': self._extraer_precio(data),
            'precio_administracion': self._extraer_precio_admin(data),
            'comodidades': self._extraer_comodidades(data),
            'caracteristicas': self._extraer_caracteristicas(technical_sheet),
            'imagenes': self._extraer_imagenes(data),
            'tipo_propiedad': self._extraer_tipo_propiedad(data),
            'inmobiliaria': self._extraer_inmobiliaria(data),
        }
        
        # Formatear a salida final
        return _formatear_salida_final(raw_data)
    
    # Métodos de extracción (copiar de property_crawler_selenium.py)
    def _extraer_ubicacion(self, data: Dict) -> Optional[str]:
        locations = data.get('locations', {})
        parts = []
        location_main = locations.get('location_main', {})
        if location_main and location_main.get('name'):
            parts.append(location_main['name'])
        city = locations.get('city', [])
        if city and len(city) > 0:
            parts.append(city[0].get('name', ''))
        state = locations.get('state', [])
        if state and len(state) > 0:
            parts.append(state[0].get('name', ''))
        if not parts and data.get('address'):
            return data['address']
        return ', '.join(p for p in parts if p)
    
    def _extraer_habitaciones(self, technical_sheet: List[Dict]) -> Optional[int]:
        if not isinstance(technical_sheet, list):
            return None
        for item in technical_sheet:
            if item.get('field') == 'bedrooms':
                value = item.get('value')
                if value:
                    try:
                        num_str = re.sub(r'[^\d]', '', str(value))
                        return int(num_str) if num_str else None
                    except (ValueError, TypeError):
                        pass
        return None
    
    def _extraer_banos(self, technical_sheet: List[Dict]) -> Optional[int]:
        if not isinstance(technical_sheet, list):
            return None
        for item in technical_sheet:
            if item.get('field') == 'bathrooms':
                value = item.get('value')
                if value:
                    try:
                        num_str = re.sub(r'[^\d]', '', str(value))
                        return int(num_str) if num_str else None
                    except (ValueError, TypeError):
                        pass
        return None
    
    def _extraer_metros(self, technical_sheet: List[Dict]) -> Optional[float]:
        if not isinstance(technical_sheet, list):
            return None
        for item in technical_sheet:
            if item.get('field') in ['m2Built', 'm2apto', 'area', 'built_area']:
                value = item.get('value')
                if value:
                    try:
                        match = re.search(r'(\d+(?:\.\d+)?)\s*m', str(value))
                        if match:
                            return float(match.group(1))
                        num_str = re.sub(r'[^\d.]', '', str(value))
                        if num_str and '.' not in num_str:
                            return float(num_str)
                    except (ValueError, TypeError):
                        pass
        return None
    
    def _extraer_precio(self, data: Dict) -> Optional[int]:
        price_obj = data.get('price', {})
        amount = price_obj.get('amount')
        if amount:
            try:
                return int(amount)
            except (ValueError, TypeError):
                pass
        return None
    
    def _extraer_precio_admin(self, data: Dict) -> Optional[int]:
        price_obj = data.get('price', {})
        admin_included = price_obj.get('admin_included')
        amount = price_obj.get('amount')
        if admin_included and amount:
            try:
                diferencia = int(admin_included) - int(amount)
                return diferencia if diferencia > 0 else None
            except (ValueError, TypeError):
                pass
        return None
    
    def _extraer_comodidades(self, data: Dict) -> List[str]:
        try:
            facilities = data.get('facilities', [])
            return [f.get('name') for f in facilities if f.get('name')]
        except Exception:
            return []
    
    def _extraer_caracteristicas(self, technical_sheet: List[Dict]) -> Dict[str, Any]:
        caracteristicas = {}
        if not isinstance(technical_sheet, list):
            return caracteristicas
        for item in technical_sheet:
            text = item.get('text')
            value = item.get('value')
            if text and value:
                caracteristicas[text] = value
        for item in technical_sheet:
            field = item.get('field', '')
            value = item.get('value')
            if field == 'tradable' and 'Acepta permuta' not in caracteristicas:
                caracteristicas['Acepta permuta'] = 'Sí' if value else 'No'
            elif field == 'remodeled' and 'Remodelado' not in caracteristicas:
                caracteristicas['Remodelado'] = 'Sí' if value else 'No'
            elif field == 'office' and 'Apto para oficina' not in caracteristicas:
                caracteristicas['Apto para oficina'] = 'Sí' if value else 'No'
            elif field == 'penthouse' and 'Penthouse' not in caracteristicas:
                caracteristicas['Penthouse'] = 'Sí' if value else 'No'
            elif field in ['pets', 'pet_friendly'] and 'Acepta mascotas' not in caracteristicas:
                caracteristicas['Acepta mascotas'] = 'Sí' if value else 'No'
            elif field in ['ambiences', 'rooms_count', 'environments'] and 'Cantidad de ambientes' not in caracteristicas:
                try:
                    num_str = re.sub(r'[^\d]', '', str(value))
                    caracteristicas['Cantidad de ambientes'] = int(num_str) if num_str else value
                except Exception:
                    caracteristicas['Cantidad de ambientes'] = value
        return caracteristicas
    
    def _extraer_imagenes(self, data: Dict) -> List[str]:
        imagenes = []
        urls_vistas = set()
        images = data.get('images', [])
        for img in images:
            if isinstance(img, dict):
                url = img.get('image')
                if url and url not in urls_vistas:
                    urls_vistas.add(url)
                    imagenes.append(url)
            elif isinstance(img, str):
                if img not in urls_vistas:
                    urls_vistas.add(img)
                    imagenes.append(img)
        if not imagenes:
            img_principal = data.get('img')
            if img_principal:
                imagenes.append(img_principal)
        return imagenes
    
    def _extraer_tipo_propiedad(self, data: Dict) -> Optional[str]:
        type_id = data.get('typeID')
        tipos = {
            1: 'Casa', 2: 'Apartamento', 3: 'Apartaestudio',
            4: 'Local', 5: 'Oficina', 6: 'Lote',
            7: 'Bodega', 8: 'Finca', 9: 'Consultorio', 10: 'Edificio',
        }
        return tipos.get(type_id)
    
    def _extraer_inmobiliaria(self, data: Dict) -> Optional[Dict[str, Any]]:
        owner = data.get('owner', {})
        if not owner:
            return None
        return {
            'id': owner.get('id'),
            'nombre': owner.get('name'),
        }
    
    def _process_url_with_retry(self, url: str, driver) -> Optional[Dict[str, Any]]:
        """Procesa una URL con reintentos automáticos"""
        for attempt in range(1, self.config['max_retries'] + 1):
            try:
                data = self._extract_property_data(driver, url)
                return data
            except Exception as e:
                if attempt < self.config['max_retries']:
                    delay = self.config['retry_delay_base'] ** attempt
                    self.logger.warning(f"Intento {attempt} falló para {url}: {e}. Reintentando en {delay}s...")
                    time.sleep(delay)
                else:
                    self.logger.error(f"Falló definitivamente {url}: {e}")
                    return None
        return None
    
    def _process_batch(self, urls: List[str], batch_num: int, total_batches: int):
        """Procesa un batch de URLs con un worker"""
        driver = None
        try:
            driver = self._create_driver()
            self.logger.info(f"Batch {batch_num}/{total_batches}: Procesando {len(urls)} URLs")
            
            for idx, url in enumerate(urls, 1):
                # Saltar si ya procesada
                if url in self.processed_urls:
                    with self.lock:
                        self.stats['skipped'] += 1
                    continue
                
                # Procesar con reintentos
                result = self._process_url_with_retry(url, driver)
                
                with self.lock:
                    if result:
                        self._append_result(result)
                        self.stats['success'] += 1
                        self.processed_urls.add(url)
                        self.logger.info(f"  [{idx}/{len(urls)}] OK: {url} (Cod FR: {result.get('Cod FR')})")
                    else:
                        self._append_result({'url': url, 'error': 'Extraction failed'}, is_error=True)
                        self.stats['failed'] += 1
                        self.failed_urls[url] = self.failed_urls.get(url, 0) + 1
                        self.logger.error(f"  [{idx}/{len(urls)}] FALLO: {url}")
                    
                    # Checkpoint periódico
                    if (self.stats['success'] + self.stats['failed']) % self.config['checkpoint_interval'] == 0:
                        self._save_checkpoint()
                
                # Pausa entre requests
                time.sleep(self.config['request_delay'])
        
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
    
    def crawl(self, urls: List[str]) -> Dict[str, Any]:
        """Crawlea lista de URLs en modo robusto y paralelo"""
        self.stats['total'] = len(urls)
        self.stats['start_time'] = datetime.now().isoformat()
        
        self.logger.info(f"{'='*70}")
        self.logger.info(f"Iniciando crawling robusto")
        self.logger.info(f"Total URLs: {len(urls)}")
        self.logger.info(f"Batch size: {self.config['batch_size']}")
        self.logger.info(f"Max workers: {self.config['max_workers']}")
        self.logger.info(f"Checkpoint cada: {self.config['checkpoint_interval']} URLs")
        self.logger.info(f"{'='*70}")
        
        # Filtrar URLs ya procesadas
        urls_pendientes = [u for u in urls if u not in self.processed_urls]
        self.logger.info(f"URLs pendientes: {len(urls_pendientes)} (ya procesadas: {len(self.processed_urls)})")
        
        # Dividir en batches
        batches = [
            urls_pendientes[i:i + self.config['batch_size']]
            for i in range(0, len(urls_pendientes), self.config['batch_size'])
        ]
        
        total_batches = len(batches)
        
        # Procesar batches con ThreadPool
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            futures = {
                executor.submit(self._process_batch, batch, idx + 1, total_batches): idx
                for idx, batch in enumerate(batches)
            }
            
            for future in as_completed(futures):
                batch_idx = futures[future]
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"Batch {batch_idx + 1} falló: {e}")
        
        # Guardar checkpoint final
        self._save_checkpoint()
        
        # Consolidar resultados en JSON único
        self._consolidate_results()
        
        # Estadísticas finales
        elapsed = (datetime.now() - datetime.fromisoformat(self.stats['start_time'])).total_seconds()
        self.stats['duration_seconds'] = elapsed
        self.stats['rate_per_second'] = self.stats['success'] / elapsed if elapsed > 0 else 0
        
        self.logger.info(f"\n{'='*70}")
        self.logger.info(f"Crawling completado")
        self.logger.info(f"  Total procesadas: {self.stats['success'] + self.stats['failed']}")
        self.logger.info(f"  Exitosas: {self.stats['success']}")
        self.logger.info(f"  Fallidas: {self.stats['failed']}")
        self.logger.info(f"  Saltadas (duplicadas): {self.stats['skipped']}")
        self.logger.info(f"  Duración: {elapsed:.1f}s")
        self.logger.info(f"  Tasa: {self.stats['rate_per_second']:.2f} props/seg")
        self.logger.info(f"{'='*70}\n")
        
        return self.stats
    
    def _consolidate_results(self):
        """Consolida JSONL a JSON único"""
        if not self.data_file.exists():
            return
        
        results = []
        with open(self.data_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    results.append(json.loads(line))
        
        output_json = self.output_dir / f'properties_{self.session_id}_consolidated.json'
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Resultados consolidados en: {output_json}")


def crawl_properties_robust(urls: List[str], output_dir: str = 'resultados', config: Dict = None) -> Dict[str, Any]:
    """
    Función principal para crawling robusto de propiedades
    
    Args:
        urls: Lista de URLs a procesar
        output_dir: Directorio de salida
        config: Diccionario con configuración personalizada
    
    Returns:
        Diccionario con estadísticas de ejecución
    """
    crawler = RobustPropertyCrawler(output_dir=output_dir, config=config)
    stats = crawler.crawl(urls)
    return stats


if __name__ == '__main__':
    # Ejemplo con 50 URLs de prueba
    urls_test = [
        "https://www.fincaraiz.com.co/casa-en-venta-en-venecia-bogota/192350837",
        "https://www.fincaraiz.com.co/apartamento-en-venta-en-centro-fontibon-bogota/192006621",
        "https://www.fincaraiz.com.co/local-en-arriendo-en-fatima-bogota/192214671",
        "https://www.fincaraiz.com.co/bodega-en-arriendo-en-alqueria-bogota/192489109",
        "https://www.fincaraiz.com.co/oficina-en-arriendo-en-potosi/192114884",
        # ... agregar más URLs
    ]
    
    # Configuración para testing (ajustar para producción)
    test_config = {
        'checkpoint_interval': 5,
        'batch_size': 10,
        'max_workers': 2,
        'headless': True,
    }
    
    stats = crawl_properties_robust(urls_test, config=test_config)
    print(f"\nEstadísticas finales: {json.dumps(stats, indent=2, ensure_ascii=False)}")
