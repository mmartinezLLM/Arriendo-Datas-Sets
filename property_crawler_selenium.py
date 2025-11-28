#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Property Crawler Alternativo - Versión Simple y Funcional
Extrae propiedades de Finca Raíz usando métodos directos
"""
import re
import json
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PropertyCrawlerSelenium:
    """Crawler simple que extrae datos directos de Finca Raíz"""
    
    def __init__(self, headless=False, user_data_dir=None):
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.driver = None
        self._init_driver()
    
    def _init_driver(self):
        """Inicializa el Chrome driver"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        # Opciones anti-detección
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        if self.user_data_dir:
            chrome_options.add_argument(f'--user-data-dir={self.user_data_dir}')
        
        # Desactivar imágenes y CSS para velocidad
        prefs = {
            'profile.default_content_setting_values.images': 2,
            'profile.managed_default_content_settings.stylesheets': 2,
        }
        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def extraer_propiedad(self, url, max_wait=30, reintentos=3):
        """Extrae datos de una propiedad con reintentos"""
        print(f"  URL: {url}")
        
        for intento in range(1, reintentos + 1):
            try:
                # Cargar la página
                self.driver.set_page_load_timeout(45)
                self.driver.get(url)
                
                # Esperar a que cargue el contenido principal
                wait = WebDriverWait(self.driver, max_wait)
                
                # Esperar por cualquiera de estos elementos
                try:
                    wait.until(EC.presence_of_element_located((By.ID, '__NEXT_DATA__')))
                except:
                    # Si no encuentra __NEXT_DATA__, espera al título o descripción
                    try:
                        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))
                    except:
                        pass
                
                time.sleep(1)
                
                html = self.driver.page_source
                
                # Intenta extraer del JSON __NEXT_DATA__
                datos = self._extraer_de_json(html, url)
                
                # Si no encuentra JSON, extrae directamente del HTML
                if not datos or not datos.get('cod_fr'):
                    datos = self._extraer_del_html(html, url)
                
                if datos and datos.get('cod_fr'):
                    print(f"    ✓ Extraído: {datos['cod_fr']}")
                    return datos
                else:
                    print(f"    ⚠ Sin datos extraídos (intento {intento}/{reintentos})")
                    
            except Exception as e:
                print(f"    ✗ Error: {str(e)[:60]} (intento {intento}/{reintentos})")
                
                if intento < reintentos:
                    time.sleep(3)
                    try:
                        self.driver.quit()
                        self._init_driver()
                    except:
                        self._init_driver()
        
        # Retorna diccionario vacío si falla
        return self._diccionario_vacio(url)
    
    def _extraer_de_json(self, html, url):
        """Extrae del JSON __NEXT_DATA__"""
        try:
            match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.+?)</script>', html, re.DOTALL)
            if not match:
                return None
            
            json_data = json.loads(match.group(1))
            props = json_data.get('props', {}).get('pageProps', {})
            data = props.get('data', {})
            technical_sheet = props.get('technicalSheet', []) or []
            
            if not data or not data.get('id'):
                return None
            
            # Extraer inmobiliaria
            owner = data.get('owner', {})
            id_inmos = owner.get('id') if owner else None
            inmos = owner.get('name') if owner else None
            
            # Extraer todos los campos en el orden especificado
            resultado = {
                'id_inmos': id_inmos,
                'inmos': inmos,
                'url_inmueble': url,
                'cod_fr': str(data.get('id', '')),
                'cod_fr_legacy': data.get('idFincaLegacy') or data.get('legacy_propID'),
                'titulo': data.get('title', ''),
                'descripcion': data.get('description', ''),
                'precio': self._parse_precio(data.get('price', {}).get('amount')),
                'precio_admin': self._parse_precio(data.get('commonExpenses', {}).get('amount')),
                'ubicacion': self._parse_ubicacion_completa(data.get('locations', {})),
                'tipo_inmueble': self._parse_tipo_inmueble_directo(data),
                'tipo_oferta': self._parse_tipo_oferta_directo(data),
                'estado': self._parse_estado_directo(technical_sheet),
                'habitaciones': self._parse_habitaciones_directo(data, technical_sheet),
                'banos': self._parse_banos_directo(data, technical_sheet),
                'parqueaderos': self._parse_parqueaderos_directo(data, technical_sheet),
                'estrato': self._parse_estrato_directo(data, technical_sheet),
                'antiguedad': self._parse_antiguedad(technical_sheet),
                'metros': data.get('m2'),
                'area': data.get('m2Built'),
                'area_privada': data.get('m2apto'),
                'area_terreno': data.get('m2Terrain'),
                'area_lote': data.get('m2'),
                'piso_no': data.get('floor'),
                'cantidad_pisos': data.get('floorsCount'),
                'cantidad_ambientes': data.get('rooms'),
                'apto_oficina': 'Sí' if data.get('office') else None,
                'acepta_permuta': 'Sí' if data.get('barter') else ('No' if data.get('barter') == False else None),
                'remodelado': self._parse_remodelado(technical_sheet),
                'penthouse': 'Sí' if data.get('penthouse') else None,
                'contrato_minimo': self._parse_contrato_minimo(technical_sheet),
                'documentacion_requerida': self._parse_documentacion(technical_sheet),
                'acepta_mascotas': self._parse_acepta_mascotas(technical_sheet),
                'm2_terraza': data.get('m2Terrace'),
                'comodidades': self._parse_comodidades(data),
                'imagenes': self._parse_imagenes_completas(data),
            }
            
            return resultado
        except Exception as e:
            print(f"    Error en JSON: {e}")
            return None
    
    def _extraer_del_html(self, html, url):
        """Extrae datos directamente del HTML si el JSON no está disponible"""
        try:
            datos = self._diccionario_vacio(url)
            
            # Intenta extraer título
            match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
            if match:
                datos['titulo'] = match.group(1).strip()
            
            # Intenta extraer descripción
            match = re.search(r'<p[^>]*class="[^"]*description[^"]*"[^>]*>([^<]+)</p>', html, re.IGNORECASE)
            if match:
                datos['descripcion'] = match.group(1).strip()
            
            # Intenta extraer precio
            match = re.search(r'\$\s*([\d,.]+)', html)
            if match:
                precio_str = match.group(1).replace('.', '').replace(',', '')
                try:
                    datos['precio'] = int(precio_str)
                except:
                    pass
            
            # Intenta extraer código de la URL
            match = re.search(r'/(\d+)[/?]', url)
            if match:
                codigo = match.group(1)
                if len(codigo) >= 6:  # Código válido de Finca Raíz
                    datos['cod_fr'] = codigo
            
            return datos
        except Exception as e:
            print(f"    Error en HTML: {e}")
            return self._diccionario_vacio(url)
    
    def _diccionario_vacio(self, url):
        """Retorna un diccionario con estructura completa"""
        return {
            'id_inmos': None,
            'inmos': None,
            'url_inmueble': url,
            'cod_fr': None,
            'cod_fr_legacy': None,
            'titulo': None,
            'descripcion': None,
            'precio': None,
            'precio_admin': None,
            'ubicacion': None,
            'tipo_inmueble': None,
            'tipo_oferta': None,
            'estado': None,
            'habitaciones': None,
            'banos': None,
            'parqueaderos': None,
            'estrato': None,
            'antiguedad': None,
            'metros': None,
            'area': None,
            'area_privada': None,
            'area_terreno': None,
            'area_lote': None,
            'piso_no': None,
            'cantidad_pisos': None,
            'cantidad_ambientes': None,
            'apto_oficina': None,
            'acepta_permuta': None,
            'remodelado': None,
            'penthouse': None,
            'contrato_minimo': None,
            'documentacion_requerida': None,
            'acepta_mascotas': None,
            'm2_terraza': None,
            'comodidades': [],
            'imagenes': [],
        }
    
    def _parse_precio(self, valor):
        if not valor:
            return None
        try:
            return int(valor)
        except:
            return None
    
    def _parse_ubicacion_completa(self, locations):
        """Extrae la ubicación completa: Barrio, Ciudad, Departamento"""
        if not locations:
            return None
        parts = []
        
        # Barrio/Neighbourhood
        neighbourhood = locations.get('location_main', {})
        if neighbourhood and neighbourhood.get('name'):
            parts.append(neighbourhood['name'])
        
        # Ciudad
        city = locations.get('city', [])
        if city and len(city) > 0 and city[0].get('name'):
            parts.append(city[0]['name'])
        
        # Departamento/Estado
        state = locations.get('state', [])
        if state and len(state) > 0 and state[0].get('name'):
            parts.append(state[0]['name'])
        
        return ', '.join(parts) if parts else None
    
    def _parse_tipo_inmueble_directo(self, data):
        """Extrae el tipo de inmueble desde property_type"""
        try:
            property_type = data.get('property_type', {})
            if property_type and property_type.get('name'):
                return property_type['name']
        except:
            pass
        return None
    
    def _parse_tipo_oferta_directo(self, data):
        """Extrae el tipo de oferta desde operation_type"""
        try:
            operation_type = data.get('operation_type', {})
            if operation_type and operation_type.get('name'):
                return operation_type['name']
        except:
            pass
        return None
    
    def _parse_estado_directo(self, sheet):
        """Extrae el estado desde construction_state_name"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') == 'construction_state_name':
                return item.get('value')
        return None
    
    def _parse_habitaciones_directo(self, data, sheet):
        """Extrae habitaciones desde data.bedrooms o technical_sheet"""
        # Primero intenta desde data
        bedrooms = data.get('bedrooms')
        if bedrooms and bedrooms > 0:
            return bedrooms
        
        # Si no, desde technical_sheet
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') == 'bedrooms':
                try:
                    val = item.get('value', '')
                    if val and str(val) != '-1' and str(val) != '':
                        num = re.sub(r'[^\d]', '', str(val))
                        return int(num) if num else None
                except:
                    pass
        return None
    
    def _parse_banos_directo(self, data, sheet):
        """Extrae baños desde data.bathrooms o technical_sheet"""
        # Primero intenta desde data
        bathrooms = data.get('bathrooms')
        if bathrooms and bathrooms > 0:
            return bathrooms
        
        # Si no, desde technical_sheet
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') == 'bathrooms':
                try:
                    val = item.get('value', '')
                    if val and str(val) != '':
                        num = re.sub(r'[^\d]', '', str(val))
                        return int(num) if num else None
                except:
                    pass
        return None
    
    def _parse_parqueaderos_directo(self, data, sheet):
        """Extrae parqueaderos desde data.garage o technical_sheet"""
        # Primero intenta desde data
        garage = data.get('garage')
        if garage and garage > 0:
            return garage
        
        # Si no, desde technical_sheet
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') == 'garage':
                try:
                    val = item.get('value', '')
                    if val and str(val) != '':
                        num = re.sub(r'[^\d]', '', str(val))
                        return int(num) if num else None
                except:
                    pass
        return None
    
    def _parse_estrato_directo(self, data, sheet):
        """Extrae estrato desde data.stratum o technical_sheet"""
        # Primero intenta desde data
        stratum = data.get('stratum')
        if stratum and stratum > 0:
            return stratum
        
        # Si no, desde technical_sheet
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') == 'stratum':
                try:
                    val = item.get('value', '')
                    if val and str(val) != '':
                        num = re.sub(r'[^\d]', '', str(val))
                        return int(num) if num else None
                except:
                    pass
        return None
    
    def _parse_habitaciones(self, sheet):
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') == 'bedrooms':
                try:
                    num = re.sub(r'[^\d]', '', str(item.get('value', '')))
                    return int(num) if num else None
                except:
                    pass
        return None
    
    def _parse_antiguedad(self, sheet):
        """Extrae la antigüedad"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['constructionYear', 'antiquity', 'antiguedad', 'age']:
                val = item.get('value', '')
                return str(val) if val and str(val) != '' else None
        return None
    
    def _parse_remodelado(self, sheet):
        """Verifica si está remodelado"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['remodeled', 'remodelado', 'renovated']:
                val = str(item.get('value', '')).lower()
                return 'Sí' if val in ['true', 'si', 'sí', 'yes', '1'] else ('No' if val else None)
        return None
    
    def _parse_contrato_minimo(self, sheet):
        """Extrae el contrato mínimo"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['minimumContract', 'contrato_minimo', 'minimum_contract']:
                val = item.get('value', '')
                return str(val) if val and str(val) != '' else None
        return None
    
    def _parse_documentacion(self, sheet):
        """Extrae la documentación requerida"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['requiredDocumentation', 'documentacion_requerida', 'required_docs']:
                val = item.get('value', '')
                return str(val) if val and str(val) != '' else None
        return None
    
    def _parse_acepta_mascotas(self, sheet):
        """Verifica si acepta mascotas"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['allowPets', 'pets', 'mascotas', 'accepts_pets', 'petFriendly']:
                val = str(item.get('value', '')).lower()
                return 'Sí' if val in ['true', 'si', 'sí', 'yes', '1'] else ('No' if val else None)
        return None
    
    def _parse_comodidades(self, data):
        """Extrae todas las comodidades separadas por |"""
        comodidades = []
        try:
            facilities = data.get('facilities', [])
            for fac in facilities:
                if fac.get('name'):
                    comodidades.append(fac['name'])
        except:
            pass
        return '|'.join(comodidades) if comodidades else None
    
    def _parse_metros(self, sheet):
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['m2Built', 'm2apto', 'area', 'built_area']:
                try:
                    match = re.search(r'(\d+(?:\.\d+)?)\s*m', str(item.get('value', '')))
                    if match:
                        return float(match.group(1))
                except:
                    pass
        return None
    
    def _parse_area(self, sheet):
        """Extrae el área total"""
        return self._parse_metros(sheet)
    
    def _parse_area_privada(self, sheet):
        """Extrae el área privada"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['privateArea', 'area_privada', 'private_area']:
                try:
                    match = re.search(r'(\d+(?:\.\d+)?)\s*m', str(item.get('value', '')))
                    if match:
                        return float(match.group(1))
                except:
                    pass
        return None
    
    def _parse_area_terreno(self, sheet):
        """Extrae el área del terreno"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['landArea', 'area_terreno', 'land_area', 'terrain_area']:
                try:
                    match = re.search(r'(\d+(?:\.\d+)?)\s*m', str(item.get('value', '')))
                    if match:
                        return float(match.group(1))
                except:
                    pass
        return None
    
    def _parse_area_lote(self, sheet):
        """Extrae el área del lote"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['lotArea', 'area_lote', 'lot_area']:
                try:
                    match = re.search(r'(\d+(?:\.\d+)?)\s*m', str(item.get('value', '')))
                    if match:
                        return float(match.group(1))
                except:
                    pass
        return None
    
    def _parse_piso_no(self, sheet):
        """Extrae el número de piso"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['floor', 'piso', 'floor_number']:
                try:
                    num = re.sub(r'[^\d]', '', str(item.get('value', '')))
                    return int(num) if num else None
                except:
                    pass
        return None
    
    def _parse_cantidad_pisos(self, sheet):
        """Extrae la cantidad de pisos del inmueble"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['floors', 'pisos', 'number_of_floors']:
                try:
                    num = re.sub(r'[^\d]', '', str(item.get('value', '')))
                    return int(num) if num else None
                except:
                    pass
        return None
    
    def _parse_cantidad_ambientes(self, sheet):
        """Extrae la cantidad de ambientes"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['rooms', 'ambientes', 'environments']:
                try:
                    num = re.sub(r'[^\d]', '', str(item.get('value', '')))
                    return int(num) if num else None
                except:
                    pass
        return None
    
    def _parse_apto_oficina(self, sheet):
        """Verifica si es apto para oficina"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['officeReady', 'apto_oficina', 'office_ready']:
                val = str(item.get('value', '')).lower()
                return 'Sí' if val in ['true', 'si', 'sí', 'yes', '1'] else 'No'
        return None
    
    def _parse_acepta_permuta(self, sheet):
        """Verifica si acepta permuta"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['exchange', 'permuta', 'accepts_exchange']:
                val = str(item.get('value', '')).lower()
                return 'Sí' if val in ['true', 'si', 'sí', 'yes', '1'] else 'No'
        return None
    
    def _parse_remodelado(self, sheet):
        """Verifica si está remodelado"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['remodeled', 'remodelado', 'renovated']:
                val = str(item.get('value', '')).lower()
                return 'Sí' if val in ['true', 'si', 'sí', 'yes', '1'] else 'No'
        return None
    
    def _parse_penthouse(self, sheet):
        """Verifica si es penthouse"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['penthouse', 'isPenthouse']:
                val = str(item.get('value', '')).lower()
                return 'Sí' if val in ['true', 'si', 'sí', 'yes', '1'] else 'No'
        return None
    
    def _parse_contrato_minimo(self, sheet):
        """Extrae el contrato mínimo"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['minimumContract', 'contrato_minimo', 'minimum_contract']:
                return str(item.get('value', ''))
        return None
    
    def _parse_documentacion(self, sheet):
        """Extrae la documentación requerida"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['requiredDocumentation', 'documentacion_requerida', 'required_docs']:
                return str(item.get('value', ''))
        return None
    
    def _parse_acepta_mascotas(self, sheet):
        """Verifica si acepta mascotas"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['pets', 'mascotas', 'accepts_pets', 'petFriendly']:
                val = str(item.get('value', '')).lower()
                return 'Sí' if val in ['true', 'si', 'sí', 'yes', '1'] else 'No'
        return None
    
    def _parse_m2_terraza(self, sheet):
        """Extrae los m² de terraza"""
        if not isinstance(sheet, list):
            return None
        for item in sheet:
            if item.get('field') in ['terraceArea', 'm2_terraza', 'terrace_area']:
                try:
                    match = re.search(r'(\d+(?:\.\d+)?)\s*m', str(item.get('value', '')))
                    if match:
                        return float(match.group(1))
                except:
                    pass
        return None
    
    def _parse_ubicacion(self, locations):
        if not locations:
            return None
        parts = []
        loc_main = locations.get('location_main', {})
        if loc_main and loc_main.get('name'):
            parts.append(loc_main['name'])
        return ', '.join(parts) if parts else None
    
    def _parse_imagenes_completas(self, data):
        """Extrae las primeras 15 imágenes desde data.images"""
        imagenes = []
        try:
            images_array = data.get('images', [])
            for img in images_array[:15]:  # Máximo 15 imágenes
                if isinstance(img, dict) and img.get('image'):
                    imagenes.append(img['image'])
                elif isinstance(img, str):
                    imagenes.append(img)
        except:
            pass
        return imagenes
    
    def _parse_comodidades(self, data):
        """Extrae todas las comodidades separadas por |"""
        comodidades = []
        try:
            facilities = data.get('facilities', [])
            for fac in facilities:
                if fac.get('name'):
                    comodidades.append(fac['name'])
        except:
            pass
        return '|'.join(comodidades) if comodidades else None
    
    def close(self):
        """Cierra el driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
