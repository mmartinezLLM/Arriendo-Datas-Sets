# Property Crawler - Finca Raíz

Crawler automatizado para extraer información detallada de propiedades desde Finca Raíz usando Selenium.

## Características

- ✅ Extracción completa de datos de propiedades
- ✅ Soporte para Selenium (JavaScript rendering)
- ✅ Manejo robusto de errores con reintentos
- ✅ Guardado incremental cada 5 URLs
- ✅ Generación de JSON y Excel
- ✅ Extracción de todas las imágenes

## Datos Extraídos

### Información Básica
- Código Finca Raíz (ID numérico y código legacy)
- Título y Meta Descripción
- H1
- Descripción completa
- Tipo de propiedad (Casa, Apartamento, etc.)

### Detalles de la Propiedad
- Ubicación (Comuna/Barrio, Ciudad, Departamento)
- Habitaciones
- Baños
- Metros cuadrados (m²)
- Precio
- Precio de administración
- Características técnicas (Estrato, Piso, Parqueaderos, Antigüedad, etc.)

### Imágenes y Multimedia
- Todas las URLs de imágenes (galería completa)
- Cantidad total de imágenes

### Información del Anunciante
- Nombre de la inmobiliaria
- ID del anunciante
- Teléfono (parcialmente oculto)
- Dirección
- Logo

## Instalación

```powershell
# Activar el entorno virtual (si no está activado)
.\.venv\Scripts\Activate.ps1

# Las dependencias ya están instaladas:
# - selenium
# - pandas
# - openpyxl
```

## Uso

### 1. Crawler con Selenium (Recomendado)

```powershell
# Ejecutar con las URLs de prueba incluidas
python .\scraper_inmobiliarias\property_crawler_selenium.py
```

**Características:**
- Modo headless (sin ventana visible)
- Manejo automático de esperas
- Extracción completa del JSON embebido
- Guardado automático en `resultados/properties_YYYYMMDD_HHMMSS.json`

### 2. Personalizar URLs

Edita el archivo `property_crawler_selenium.py` y modifica la lista `urls_prueba`:

```python
urls_prueba = [
    "https://www.fincaraiz.com.co/apartamento-en-venta-...",
    "https://www.fincaraiz.com.co/casa-en-arriendo-...",
    # Agrega más URLs aquí
]
```

### 3. Modo con navegador visible

```python
# En property_crawler_selenium.py, cambia:
resultados = crawlear_propiedades(urls_prueba, output, headless=False)
```

### 4. Convertir JSON a Excel

```powershell
# Usar el último JSON generado automáticamente
python .\scraper_inmobiliarias\json_to_excel_properties.py

# O especificar archivo
python .\scraper_inmobiliarias\json_to_excel_properties.py resultados\properties_20251114_084828.json
```

## Estructura de Archivos

```
scraper_inmobiliarias/
├── property_crawler_selenium.py    # Crawler principal con Selenium
├── json_to_excel_properties.py     # Convertidor JSON → Excel
└── resultados/                      # Carpeta de resultados
    ├── properties_*.json            # JSONs generados
    └── properties_excel_*.xlsx      # Excels generados
```

## Formato de Salida

### JSON
```json
[
  {
    "url": "https://www.fincaraiz.com.co/...",
    "codigo_fr": "192454261",
    "codigo_fr_legacy": "FRBD6373",
    "meta_titulo": "Apartamento en Venta...",
    "tipo_propiedad": "Apartamento",
    "ubicacion": "Comuna 12 - cabecera del llano, Bucaramanga, Santander",
    "habitaciones": 4,
    "banos": 4,
    "metros": 273.0,
    "precio": 800000000,
    "precio_administracion": 1200000,
    "caracteristicas": {
      "Tipo de Inmueble": "Apartamento",
      "Estado": "Usado",
      "Estrato": "5",
      ...
    },
    "imagenes": [
      "https://cdn2.infocasas.com.uy/repo/img/...",
      ...
    ],
    "inmobiliaria": {
      "id": 174802444,
      "nombre": "Urbacon de Colombia",
      ...
    }
  }
]
```

### Excel
- **Columnas principales:** codigo_fr, titulo, tipo_propiedad, ubicacion, habitaciones, banos, metros_m2, precio, etc.
- **Columnas de características:** caract_Estado, caract_Estrato, caract_Parqueaderos, etc.
- **Imágenes:** columnas num_imagenes, imagen_principal, imagenes_urls (todas las URLs)

## Ejemplos de Resultados

### Propiedad Exitosa
```
Propiedad 1:
  Codigo FR: 192454261
  Titulo: Apartamento en Venta en Comuna 12 - cabecera del llano, Bucaramanga
  Ubicacion: Comuna 12 - cabecera del llano, Bucaramanga, Santander
  Tipo: Apartamento
  Habitaciones: 4, Baños: 4, Metros: 273.0 m2
  Precio: $800,000,000
  Administración: $1,200,000
  Características: 11 items
  Imágenes: 20 URLs
  Inmobiliaria: Urbacon de Colombia
```

## Configuración Avanzada

### Cambiar tiempo de espera
```python
# En property_crawler_selenium.py
datos = crawler.extraer_propiedad(url, max_wait=20)  # 20 segundos
```

### Desactivar carga de imágenes (más rápido)
Ya está configurado por defecto en el crawler para mejor rendimiento.

### Usar perfil de Chrome específico
```python
crawler = PropertyCrawlerSelenium(
    headless=True,
    user_data_dir="C:/Users/Tu/AppData/Local/Google/Chrome/User Data"
)
```

## Solución de Problemas

### "No se encontró __NEXT_DATA__"
- La página no cargó completamente
- Aumenta `max_wait` en `extraer_propiedad()`

### "TimeoutException"
- Conexión lenta
- Aumenta el tiempo de espera
- Verifica tu conexión a internet

### Errores de ChromeDriver
- Asegúrate de tener Chrome instalado
- Selenium descarga automáticamente el driver correcto

### Excel con encoding incorrecto
- Los archivos se generan con UTF-8
- Abrir con Excel puede mostrar caracteres raros
- Solución: Import Data > From File en Excel

## Notas Importantes

1. **Velocidad**: El crawler procesa aproximadamente 1 propiedad cada 3-5 segundos
2. **Guardado incremental**: Se guarda progreso cada 5 URLs procesadas
3. **Headless**: Por defecto ejecuta sin mostrar el navegador
4. **Imágenes**: Extrae TODAS las imágenes de la galería (10-20+ por propiedad)
5. **Características**: Se extraen dinámicamente todas las características disponibles

## Próximas Mejoras Sugeridas

- [ ] Soporte para leer URLs desde Excel/CSV
- [ ] Paralelización con múltiples instancias de Chrome
- [ ] Filtrado de propiedades por criterios
- [ ] Detección de duplicados
- [ ] Notificaciones por email al finalizar

## Autor

Creado para extracción masiva de datos de propiedades desde Finca Raíz.
Fecha: Noviembre 2025
