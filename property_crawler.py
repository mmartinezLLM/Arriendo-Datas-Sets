"""
property_crawler.py - Crawler de propiedades de Finca Raíz
Extrae todos los datos de una propiedad usando requests + BeautifulSoup
"""
import re
import json
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any


class PropertyCrawler:
    """Crawler para extraer datos de propiedades de Finca Raíz"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-CO,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def extraer_propiedad(self, url: str) -> Dict[str, Any]:
        """
        Extrae todos los datos de una propiedad
        
        Args:
            url: URL de la propiedad en Finca Raíz
            
        Returns:
            Diccionario con todos los datos extraídos
        """
        print(f"Crawleando: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            datos = {
                'url': url,
                'codigo_fr': self._extraer_codigo_fr(soup, response.text),
                'meta_titulo': self._extraer_meta_titulo(soup),
                'meta_descripcion': self._extraer_meta_descripcion(soup),
                'h1': self._extraer_h1(soup),
                'descripcion': self._extraer_descripcion(soup),
                'ubicacion': self._extraer_ubicacion(soup),
                'habitaciones': self._extraer_habitaciones(soup),
                'banos': self._extraer_banos(soup),
                'metros': self._extraer_metros(soup),
                'precio': self._extraer_precio(soup),
                'precio_administracion': self._extraer_precio_administracion(soup),
                'comodidades': self._extraer_comodidades(soup),
                'caracteristicas': self._extraer_caracteristicas(soup),
                'imagenes': self._extraer_imagenes(soup, response.text),
            }
            
            print(f"  OK Codigo FR: {datos['codigo_fr']}")
            print(f"  OK Precio: {datos['precio']}")
            print(f"  OK Imagenes encontradas: {len(datos['imagenes'])}")
            
            return datos
            
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}")
            return {
                'url': url,
                'error': str(e),
                'tipo_error': type(e).__name__
            }
    
    def _extraer_codigo_fr(self, soup: BeautifulSoup, html: str) -> Optional[str]:
        """Extrae el código FR del inmueble"""
        # Buscar en el texto "Código Fincaraíz: XXXXXXXX"
        match = re.search(r'Código Fincaraíz:\s*(\d+)', html)
        if match:
            return match.group(1)
        
        # Alternativa: extraer de la URL
        match = re.search(r'/(\d+)/?$', soup.find('link', {'rel': 'canonical'})['href'] if soup.find('link', {'rel': 'canonical'}) else '')
        return match.group(1) if match else None
    
    def _extraer_meta_titulo(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae el meta título (og:title o title)"""
        # Intentar Open Graph title
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Fallback a <title>
        title_tag = soup.find('title')
        return title_tag.text.strip() if title_tag else None
    
    def _extraer_meta_descripcion(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae la meta descripción"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # Alternativa: og:description
        og_desc = soup.find('meta', property='og:description')
        return og_desc['content'].strip() if og_desc and og_desc.get('content') else None
    
    def _extraer_h1(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae el primer H1 de la página"""
        h1 = soup.find('h1')
        return h1.text.strip() if h1 else None
    
    def _extraer_descripcion(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae la descripción completa del inmueble"""
        # Buscar sección de descripción
        desc_section = None
        
        # Intentar encontrar por texto "Descripción"
        for header in soup.find_all(['h2', 'h3', 'h4']):
            if 'descripción' in header.text.lower():
                # Buscar el contenedor padre que tenga el texto
                parent = header.find_parent()
                if parent:
                    # Buscar párrafos dentro del contenedor
                    paragraphs = parent.find_all('p')
                    if paragraphs:
                        desc_texts = [p.get_text(strip=True) for p in paragraphs]
                        descripcion = ' '.join(desc_texts)
                        # Limpiar código FR si aparece
                        descripcion = re.sub(r'Código Fincaraíz:\s*\d+', '', descripcion).strip()
                        return descripcion if descripcion else None
        
        return None
    
    def _extraer_ubicacion(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae la ubicación del inmueble"""
        # Buscar sección de ubicación
        for header in soup.find_all(['h2', 'h3', 'h4']):
            if 'ubicación' in header.text.lower():
                parent = header.find_parent()
                if parent:
                    # Buscar texto después del header
                    ubicacion_text = parent.get_text(separator=' ', strip=True)
                    # Limpiar el texto del header
                    ubicacion_text = ubicacion_text.replace('Ubicación', '').strip()
                    # Tomar solo las primeras líneas antes de "Leaflet" o mapas
                    ubicacion_text = re.split(r'Leaflet|Ver mapa', ubicacion_text)[0].strip()
                    return ubicacion_text if ubicacion_text else None
        
        return None
    
    def _extraer_habitaciones(self, soup: BeautifulSoup) -> Optional[int]:
        """Extrae el número de habitaciones"""
        # Buscar en detalles de la propiedad
        texto = soup.get_text()
        
        # Buscar patrones como "4 Habs." o "Habitaciones 4"
        match = re.search(r'(\d+)\s*Habs?\.?', texto)
        if match:
            return int(match.group(1))
        
        match = re.search(r'Habitaciones\s*(\d+)', texto)
        if match:
            return int(match.group(1))
        
        return None
    
    def _extraer_banos(self, soup: BeautifulSoup) -> Optional[int]:
        """Extrae el número de baños"""
        texto = soup.get_text()
        
        # Buscar patrones como "4 Baños" o "Baños 4"
        match = re.search(r'(\d+)\s*Baños?', texto)
        if match:
            return int(match.group(1))
        
        match = re.search(r'Baños\s*(\d+)', texto)
        if match:
            return int(match.group(1))
        
        return None
    
    def _extraer_metros(self, soup: BeautifulSoup) -> Optional[float]:
        """Extrae los metros cuadrados"""
        texto = soup.get_text()
        
        # Buscar patrones como "273m²" o "273 m²" o "Área Construida 273 m2"
        match = re.search(r'(\d+(?:\.\d+)?)\s*m[²2]', texto)
        if match:
            return float(match.group(1))
        
        match = re.search(r'Área\s+(?:Construida|Privada)\s+(\d+(?:\.\d+)?)', texto)
        if match:
            return float(match.group(1))
        
        return None
    
    def _extraer_precio(self, soup: BeautifulSoup) -> Optional[int]:
        """Extrae el precio del inmueble"""
        texto = soup.get_text()
        
        # Buscar patrones como "$ 800.000.000" (antes de "administración")
        # Primero intentar precio con contexto "Precio de Venta" o similar
        match = re.search(r'Precio\s+de\s+(?:Venta|Arriendo)[:\s]*\$\s*([\d.]+)', texto)
        if match:
            precio_str = match.group(1).replace('.', '')
            return int(precio_str)
        
        # Buscar el primer precio grande (> 1 millón)
        matches = re.findall(r'\$\s*([\d.]+)', texto)
        for precio_str in matches:
            precio_num = precio_str.replace('.', '')
            try:
                precio = int(precio_num)
                if precio > 1000000:  # Filtrar precios pequeños (probablemente administración)
                    return precio
            except ValueError:
                continue
        
        return None
    
    def _extraer_precio_administracion(self, soup: BeautifulSoup) -> Optional[int]:
        """Extrae el precio de administración si existe"""
        texto = soup.get_text()
        
        # Buscar "$ X.XXX.XXX administración" o "Administración $ X.XXX.XXX"
        match = re.search(r'[+\s]*\$\s*([\d.]+)\s+administración', texto, re.IGNORECASE)
        if match:
            precio_str = match.group(1).replace('.', '')
            return int(precio_str)
        
        match = re.search(r'Administración\s*\$\s*([\d.]+)', texto, re.IGNORECASE)
        if match:
            precio_str = match.group(1).replace('.', '')
            return int(precio_str)
        
        return None
    
    def _extraer_comodidades(self, soup: BeautifulSoup) -> List[str]:
        """Extrae la lista de comodidades"""
        comodidades = []
        
        # Buscar sección de comodidades
        for header in soup.find_all(['h2', 'h3', 'h4']):
            if 'comodidades' in header.text.lower():
                parent = header.find_parent()
                if parent:
                    # Buscar todos los items (li, span, etc.)
                    items = parent.find_all(['li', 'span'])
                    for item in items:
                        texto = item.get_text(strip=True)
                        # Filtrar elementos vacíos y headers
                        if texto and len(texto) > 2 and 'comodidades' not in texto.lower():
                            # Limpiar bullets y símbolos
                            texto = texto.replace('•', '').strip()
                            if texto and texto not in comodidades:
                                comodidades.append(texto)
        
        return comodidades
    
    def _extraer_caracteristicas(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extrae las características/detalles de la propiedad"""
        caracteristicas = {}
        
        # Buscar sección "Detalles de la Propiedad"
        for header in soup.find_all(['h2', 'h3', 'h4']):
            if 'detalles' in header.text.lower() and 'propiedad' in header.text.lower():
                parent = header.find_parent()
                if parent:
                    # Buscar todos los items con formato "Clave: Valor"
                    items = parent.find_all(['li', 'div', 'span'])
                    for item in items:
                        texto = item.get_text(strip=True)
                        # Buscar pares clave-valor
                        if ':' in texto or '  ' in texto:
                            # Limpiar bullets
                            texto = texto.replace('•', '').strip()
                            # Intentar separar por ':'
                            if ':' in texto:
                                partes = texto.split(':', 1)
                            else:
                                # Separar por espacios múltiples
                                partes = re.split(r'\s{2,}', texto, 1)
                            
                            if len(partes) == 2:
                                clave = partes[0].strip()
                                valor = partes[1].strip()
                                if clave and valor:
                                    caracteristicas[clave] = valor
        
        return caracteristicas
    
    def _extraer_imagenes(self, soup: BeautifulSoup, html: str) -> List[str]:
        """Extrae todas las URLs de imágenes del inmueble"""
        imagenes = []
        urls_vistas = set()
        
        # Método 1: Buscar en tags <img> con src que contengan fincaraiz o repo
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src and ('fincaraiz' in src or 'repo' in src or 'cdn' in src):
                # Filtrar logos y iconos pequeños
                if not any(x in src.lower() for x in ['logo', 'icon', 'arrow', 'svg']):
                    if src not in urls_vistas:
                        urls_vistas.add(src)
                        imagenes.append(src)
        
        # Método 2: Buscar en el HTML directamente URLs de imágenes
        # Patrón para URLs de CDN de Finca Raíz
        patron_cdn = r'https://cdn\d*\.fincaraiz\.com\.co/[^"\s]+'
        matches = re.findall(patron_cdn, html)
        for url in matches:
            # Filtrar extensiones de imagen
            if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                if url not in urls_vistas:
                    urls_vistas.add(url)
                    imagenes.append(url)
        
        # Método 3: Buscar en data-src, data-lazy, etc.
        for img in soup.find_all('img'):
            for attr in ['data-src', 'data-lazy', 'data-original']:
                src = img.get(attr, '')
                if src and src not in urls_vistas:
                    if 'fincaraiz' in src or 'cdn' in src:
                        urls_vistas.add(src)
                        imagenes.append(src)
        
        return imagenes


def crawlear_propiedades(urls: List[str], output_file: str = None) -> List[Dict]:
    """
    Crawlea una lista de URLs de propiedades
    
    Args:
        urls: Lista de URLs a procesar
        output_file: Ruta del archivo de salida (opcional)
        
    Returns:
        Lista de diccionarios con los datos extraídos
    """
    crawler = PropertyCrawler()
    resultados = []
    
    print(f"\n{'='*70}")
    print(f"Iniciando crawling de {len(urls)} propiedades")
    print(f"{'='*70}\n")
    
    for idx, url in enumerate(urls, 1):
        print(f"\n[{idx}/{len(urls)}]")
        datos = crawler.extraer_propiedad(url)
        resultados.append(datos)
        
        # Guardar progreso cada 5 URLs
        if output_file and idx % 5 == 0:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)
            print(f"  [GUARDADO] Progreso guardado ({idx} URLs procesadas)")
    
    # Guardar resultados finales
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        print(f"\nOK Resultados guardados en: {output_file}")
    
    return resultados


if __name__ == '__main__':
    # URLs de prueba
    urls_prueba = [
        "https://www.fincaraiz.com.co/apartamento-en-venta-en-comuna-12-cabecera-del-llano-bucaramanga/192454261",
        "https://www.fincaraiz.com.co/casa-en-venta-en-venecia-bogota/192350837",
        "https://www.fincaraiz.com.co/apartamento-en-venta-en-centro-fontibon-bogota/192006621",
        "https://www.fincaraiz.com.co/casa-lote-en-venta-en-patio-bonito-bogota/193098906"
    ]
    
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output = f'resultados/properties_{timestamp}.json'
    
    resultados = crawlear_propiedades(urls_prueba, output)
    
    print(f"\n{'='*70}")
    print(f"Resumen:")
    print(f"  Total procesadas: {len(resultados)}")
    exitosas = sum(1 for r in resultados if 'error' not in r)
    print(f"  Exitosas: {exitosas}")
    print(f"  Fallidas: {len(resultados) - exitosas}")
    print(f"{'='*70}\n")
