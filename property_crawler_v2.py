"""
property_crawler_v2.py - Crawler optimizado para Finca Raíz
Extrae datos del JSON embebido en las páginas Next.js
"""
import re
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class PropertyCrawlerV2:
    """Crawler que extrae datos del JSON de Next.js en Finca Raíz"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-CO,es;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        })
    
    def extraer_propiedad(self, url: str) -> Dict[str, Any]:
        """
        Extrae todos los datos de una propiedad desde el JSON Next.js
        
        Args:
            url: URL de la propiedad en Finca Raíz
            
        Returns:
            Diccionario con todos los datos extraídos
        """
        print(f"Crawleando: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            print(f"    DEBUG: Status {response.status_code}, Content-Length: {len(response.text)}")
            print(f"    DEBUG: Content-Type: {response.headers.get('content-type')}")
            
            # Extraer el JSON de __NEXT_DATA__
            json_data = self._extraer_next_data(response.text)
            
            if not json_data:
                raise ValueError("No se encontro __NEXT_DATA__ en la pagina")
            
            # Extraer datos de la estructura Next.js
            page_props = json_data.get('props', {}).get('pageProps', {})
            data = page_props.get('data', {})
            technical_sheet = page_props.get('technicalSheet', {})
            
            if not data:
                raise ValueError("No se encontraron datos de propiedad en pageProps")
            
            # Extraer todos los campos
            resultado = {
                'url': url,
                'codigo_fr': str(data.get('id')),
                'codigo_fr_legacy': data.get('code'),
                'meta_titulo': data.get('title'),
                'meta_descripcion': self._extraer_meta_descripcion(data),
                'h1': data.get('title'),  # El title es el h1 en estas páginas
                'descripcion': data.get('description'),
                'ubicacion': self._extraer_ubicacion(data),
                'habitaciones': self._extraer_habitaciones(technical_sheet),
                'banos': self._extraer_banos(technical_sheet),
                'metros': self._extraer_metros(technical_sheet),
                'precio': self._extraer_precio(data),
                'precio_administracion': self._extraer_precio_admin(data),
                'comodidades': self._extraer_comodidades(technical_sheet),
                'caracteristicas': self._extraer_caracteristicas(technical_sheet),
                'imagenes': self._extraer_imagenes(data, page_props),
                'tipo_propiedad': self._extraer_tipo_propiedad(data),
                'inmobiliaria': self._extraer_inmobiliaria(data),
            }
            
            print(f"  OK Codigo FR: {resultado['codigo_fr']}")
            print(f"  OK Precio: ${resultado['precio']:,}" if resultado['precio'] else "  OK Precio: None")
            print(f"  OK Imagenes: {len(resultado['imagenes'])}")
            
            return resultado
            
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}")
            return {
                'url': url,
                'error': str(e),
                'tipo_error': type(e).__name__
            }
    
    def _extraer_next_data(self, html: str) -> Optional[Dict]:
        """Extrae y parsea el JSON de __NEXT_DATA__"""
        # Debug: verificar si está en el HTML
        has_next_data = '__NEXT_DATA__' in html
        print(f"    DEBUG: __NEXT_DATA__ en HTML: {has_next_data}, longitud: {len(html)}")
        
        # Patrón flexible que acepta atributos adicionales como crossorigin
        match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.+?)</script>', html, re.DOTALL)
        print(f"    DEBUG: Match encontrado: {match is not None}")
        
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError as e:
                print(f"    DEBUG: Error JSON: {e}")
                return None
        return None
    
    def _extraer_meta_descripcion(self, data: Dict) -> Optional[str]:
        """Extrae la meta descripción (resumen corto)"""
        # Tomar las primeras 160 caracteres de la descripción como meta
        desc = data.get('description', '')
        if desc:
            return desc[:160] + '...' if len(desc) > 160 else desc
        return None
    
    def _extraer_ubicacion(self, data: Dict) -> Optional[str]:
        """Extrae la ubicación completa"""
        # Combinar información de locations
        locations = data.get('locations', {})
        
        parts = []
        
        # Comuna/Barrio
        location_main = locations.get('location_main', {})
        if location_main and location_main.get('name'):
            parts.append(location_main['name'])
        
        # Ciudad
        city = locations.get('city', [])
        if city and len(city) > 0:
            parts.append(city[0].get('name', ''))
        
        # Departamento
        state = locations.get('state', [])
        if state and len(state) > 0:
            parts.append(state[0].get('name', ''))
        
        # Alternativamente usar address
        if not parts and data.get('address'):
            return data['address']
        
        return ', '.join(p for p in parts if p)
    
    def _extraer_habitaciones(self, technical_sheet: Dict) -> Optional[int]:
        """Extrae número de habitaciones"""
        general_features = technical_sheet.get('general_features', [])
        for feature in general_features:
            if feature.get('code') == 'bedrooms':
                value = feature.get('value')
                if value:
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        pass
        return None
    
    def _extraer_banos(self, technical_sheet: Dict) -> Optional[int]:
        """Extrae número de baños"""
        general_features = technical_sheet.get('general_features', [])
        for feature in general_features:
            if feature.get('code') == 'bathrooms':
                value = feature.get('value')
                if value:
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        pass
        return None
    
    def _extraer_metros(self, technical_sheet: Dict) -> Optional[float]:
        """Extrae metros cuadrados (área construida o total)"""
        general_features = technical_sheet.get('general_features', [])
        
        # Priorizar área construida
        for feature in general_features:
            if feature.get('code') in ['built_area', 'area']:
                value = feature.get('value')
                if value:
                    try:
                        # Limpiar texto como "273 m²"
                        num_str = re.sub(r'[^\d.]', '', str(value))
                        return float(num_str) if num_str else None
                    except (ValueError, TypeError):
                        pass
        
        return None
    
    def _extraer_precio(self, data: Dict) -> Optional[int]:
        """Extrae el precio principal"""
        price_obj = data.get('price', {})
        amount = price_obj.get('amount')
        
        if amount:
            try:
                return int(amount)
            except (ValueError, TypeError):
                pass
        
        return None
    
    def _extraer_precio_admin(self, data: Dict) -> Optional[int]:
        """Extrae el precio de administración"""
        price_obj = data.get('price', {})
        
        # Calcular diferencia entre admin_included y amount
        admin_included = price_obj.get('admin_included')
        amount = price_obj.get('amount')
        
        if admin_included and amount:
            try:
                diferencia = int(admin_included) - int(amount)
                return diferencia if diferencia > 0 else None
            except (ValueError, TypeError):
                pass
        
        return None
    
    def _extraer_comodidades(self, technical_sheet: Dict) -> List[str]:
        """Extrae lista de comodidades"""
        comodidades = []
        
        # Buscar en amenities o features
        amenities = technical_sheet.get('amenities', [])
        for amenity in amenities:
            name = amenity.get('name') or amenity.get('label')
            if name and name not in comodidades:
                comodidades.append(name)
        
        return comodidades
    
    def _extraer_caracteristicas(self, technical_sheet: Dict) -> Dict[str, Any]:
        """Extrae características técnicas de la propiedad"""
        caracteristicas = {}
        
        # General features
        general_features = technical_sheet.get('general_features', [])
        for feature in general_features:
            name = feature.get('name') or feature.get('label')
            value = feature.get('value')
            if name and value:
                caracteristicas[name] = value
        
        # Property characteristics
        prop_chars = technical_sheet.get('property_characteristics', [])
        for char in prop_chars:
            name = char.get('name') or char.get('label')
            value = char.get('value')
            if name and value:
                caracteristicas[name] = value
        
        # Additional details
        details = technical_sheet.get('details', [])
        for detail in details:
            name = detail.get('name') or detail.get('label')
            value = detail.get('value')
            if name and value:
                caracteristicas[name] = value
        
        return caracteristicas
    
    def _extraer_imagenes(self, data: Dict, page_props: Dict) -> List[str]:
        """Extrae todas las URLs de imágenes"""
        imagenes = []
        urls_vistas = set()
        
        # Método 1: Imagen principal
        img_principal = data.get('img')
        if img_principal and img_principal not in urls_vistas:
            urls_vistas.add(img_principal)
            imagenes.append(img_principal)
        
        # Método 2: Buscar en media o gallery
        media = data.get('media', [])
        for item in media:
            url = item.get('url') or item.get('src') or item.get('image')
            if url and url not in urls_vistas:
                urls_vistas.add(url)
                imagenes.append(url)
        
        # Método 3: Buscar en images
        images = data.get('images', [])
        for img in images:
            if isinstance(img, str):
                url = img
            else:
                url = img.get('url') or img.get('src')
            
            if url and url not in urls_vistas:
                urls_vistas.add(url)
                imagenes.append(url)
        
        # Método 4: Buscar gallery en page_props
        gallery = page_props.get('gallery', [])
        for item in gallery:
            url = item.get('url') or item.get('src') or item.get('image')
            if url and url not in urls_vistas:
                urls_vistas.add(url)
                imagenes.append(url)
        
        return imagenes
    
    def _extraer_tipo_propiedad(self, data: Dict) -> Optional[str]:
        """Extrae el tipo de propiedad (apartamento, casa, etc.)"""
        type_id = data.get('typeID')
        
        # Mapeo de IDs a nombres (basado en Finca Raíz)
        tipos = {
            1: 'Casa',
            2: 'Apartamento',
            3: 'Apartaestudio',
            4: 'Local',
            5: 'Oficina',
            6: 'Lote',
            7: 'Bodega',
            8: 'Finca',
            9: 'Consultorio',
            10: 'Edificio',
        }
        
        return tipos.get(type_id)
    
    def _extraer_inmobiliaria(self, data: Dict) -> Optional[Dict[str, Any]]:
        """Extrae información de la inmobiliaria"""
        owner = data.get('owner', {})
        
        if not owner:
            return None
        
        return {
            'id': owner.get('id'),
            'nombre': owner.get('name'),
            'tipo': owner.get('type'),
            'telefono': owner.get('masked_phone'),
            'direccion': owner.get('address'),
            'logo': owner.get('logo'),
        }


def crawlear_propiedades(urls: List[str], output_file: str = None) -> List[Dict]:
    """
    Crawlea una lista de URLs de propiedades
    
    Args:
        urls: Lista de URLs a procesar
        output_file: Ruta del archivo de salida JSON (opcional)
        
    Returns:
        Lista de diccionarios con los datos extraídos
    """
    crawler = PropertyCrawlerV2()
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
    
    # Generar resumen
    print(f"\n{'='*70}")
    print(f"Resumen:")
    print(f"  Total procesadas: {len(resultados)}")
    exitosas = sum(1 for r in resultados if 'error' not in r)
    print(f"  Exitosas: {exitosas}")
    print(f"  Fallidas: {len(resultados) - exitosas}")
    print(f"{'='*70}\n")
    
    return resultados


if __name__ == '__main__':
    # URLs de prueba
    urls_prueba = [
        "https://www.fincaraiz.com.co/apartamento-en-venta-en-comuna-12-cabecera-del-llano-bucaramanga/192454261",
        "https://www.fincaraiz.com.co/apartamento-en-venta-en-lagos-del-cacique-bucaramanga/192955110",
        "https://www.fincaraiz.com.co/apartamento-en-arriendo-en-prados-de-catalu%C3%B1a-giron/192972546",
    ]
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output = f'resultados/properties_{timestamp}.json'
    
    resultados = crawlear_propiedades(urls_prueba, output)
