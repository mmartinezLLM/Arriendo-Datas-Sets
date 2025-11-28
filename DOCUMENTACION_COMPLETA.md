# 📋 DOCUMENTACIÓN COMPLETA - Scraper de Inmobiliarias FinCaRaíz

## 🎯 Resumen del Proyecto

Has recibido un **sistema completo de web scraping y crawling** diseñado específicamente para extraer información de inmobiliarias del sitio fincaraiz.com.co.

### Características Principales:

✅ **Extracción Automatizada**
- Título de la inmobiliaria
- Correo electrónico
- Número de teléfono (con manejo de elementos interactivos)
- Cantidad de inmuebles
- URL del perfil

✅ **Navegador Automatizado**
- Soporte para Chrome y Firefox
- Modo headless (sin ventana) o con interfaz gráfica
- User Agent configurable
- Manejo automático de timeouts

✅ **Extracción Inteligente**
- Detección automática de estructura de página
- Múltiples estrategias de búsqueda de elementos
- Manejo de elementos interactivos (botones, modales)
- Scroll automático para cargar más elementos

✅ **Guardado Flexible**
- CSV (para Excel/bases de datos)
- JSON (para APIs/aplicaciones)
- Excel (con formato automático)

✅ **Logging Detallado**
- Logs en archivo y consola
- Rastreo completo de operaciones
- Reportes de inspección para debugging

---

## 📁 Estructura del Proyecto

```
scraper_inmobiliarias/
│
├── 🚀 Scripts Principales
│   ├── main_fincaraiz.py          ← Script principal recomendado
│   ├── main.py                     ← Versión básica
│   ├── selector_inspector.py       ← Herramienta de inspección
│   └── setup_and_run.py            ← Menú interactivo
│
├── ⚙️ Módulos Core
│   ├── config.py                   ← Configuración global
│   ├── logger_config.py            ← Sistema de logging
│   ├── browser_manager.py          ← Gestor de Selenium
│   ├── extractor.py                ← Extractor básico
│   ├── advanced_extractor.py       ← Extractor avanzado con interacciones
│   ├── fincaraiz_adapter.py        ← Adaptador específico para fincaraiz
│   └── data_saver.py               ← Guardado de datos
│
├── 📚 Documentación
│   ├── README.md                   ← Documentación completa
│   ├── GUIA_RAPIDA.md              ← Guía de inicio rápido
│   └── DOCUMENTACION_COMPLETA.md   ← Este archivo
│
├── 📦 Configuración
│   ├── requirements.txt            ← Dependencias Python
│   ├── .env.example                ← Variables de entorno
│   └── config.py                   ← Configuración personalizable
│
└── 📁 Carpeta de Resultados (se crea automáticamente)
    resultados/
    ├── inmobiliarias_*.csv
    ├── inmobiliarias_*.json
    ├── inmobiliarias_*.xlsx
    ├── scraper.log
    ├── inspection_report.json
    └── detection_report.json
```

---

## 🔧 Instalación Paso a Paso

### Paso 1: Verificar Python

```powershell
python --version
# Debe ser Python 3.8 o superior
```

### Paso 2: Instalar Dependencias

```powershell
cd "c:\Users\Miguel Martinez SSD\OneDrive - BROWSER TRAVEL SOLUTIONS S.A.S VIAJEMOS\Documentos\PROYECTOS\ARRIENDO DATA SETS\scraper_inmobiliarias"

pip install -r requirements.txt
```

**Dependencias que se instalarán:**
- `selenium` - Automatización de navegador
- `beautifulsoup4` - Análisis HTML
- `webdriver-manager` - Gestión automática de drivers
- `pandas` - Manipulación de datos
- `requests` - Cliente HTTP
- `python-dotenv` - Manejo de variables de entorno

### Paso 3: Verificar Instalación

```powershell
python -c "import selenium; print('✓ Selenium instalado')"
python -c "import bs4; print('✓ BeautifulSoup4 instalado')"
python -c "import pandas; print('✓ Pandas instalado')"
```

---

## 🚀 Uso Básico

### Opción 1: Menú Interactivo (Recomendado)

```powershell
python setup_and_run.py
```

Luego selecciona:
1. Instalar dependencias
2. Inspeccionar estructura
3. Ejecutar scraper

### Opción 2: Comando Directo

```powershell
# Ejecución simple
python main_fincaraiz.py

# Con salida detallada
python main_fincaraiz.py -v
```

### Opción 3: Inspeccionar Primero

```powershell
# Paso 1: Inspeccionar la página
python selector_inspector.py

# Esto genera: resultados/inspection_report.json

# Paso 2: Revisar el reporte en resultados/inspection_report.json

# Paso 3: Ejecutar scraper
python main_fincaraiz.py
```

---

## ⚙️ Configuración Personalizada

Edita `config.py` para personalizar el comportamiento:

### Configuración Recomendada para Principiantes

```python
# config.py

# Mostrar el navegador (Para ver qué sucede)
HEADLESS = False  # Cambiar a True para ejecutar sin ventana

# Tipo de navegador
BROWSER_TYPE = "chrome"  # Más rápido, más compatible

# Formato de salida
OUTPUT_FORMAT = "csv"  # Fácil de abrir en Excel

# Tiempos
IMPLICIT_WAIT = 15  # Espera más para conexiones lentas
PAGE_LOAD_TIMEOUT = 40
SCROLL_PAUSE_TIME = 2
```

### Configuración para Producción

```python
# config.py

# Sin interfaz gráfica
HEADLESS = True

# Mejor rendimiento
BROWSER_TYPE = "chrome"

# Guarda en Excel para análisis
OUTPUT_FORMAT = "excel"

# Más robusto
IMPLICIT_WAIT = 20
PAGE_LOAD_TIMEOUT = 50
MAX_RETRIES = 5
```

### Configuración para Debugging

```python
# config.py

# Ver lo que pasa
HEADLESS = False

# Firefox es más lento pero más visible
BROWSER_TYPE = "firefox"

# Guardar en JSON para inspeccionar estructura
OUTPUT_FORMAT = "json"

# Más tiempo para investigar
IMPLICIT_WAIT = 30
```

---

## 📊 Ejemplos de Datos Extraídos

### Estructura de Datos

Cada inmobiliaria tendrá esta estructura:

```json
{
  "titulo": "Inmobiliaria Premium S.A.S",
  "correo": "contacto@inmobiliaria.com.co",
  "telefono": "+57 1 5551234 o Requiere inicio de sesión",
  "cantidad_inmuebles": 237,
  "url": "https://www.fincaraiz.com.co/inmobiliarias/inmobiliaria-premium"
}
```

### Formatos de Salida

**CSV (Para Excel):**
```
titulo,correo,telefono,cantidad_inmuebles,url
Inmobiliaria Premium,contacto@inmobiliaria.com,+57 1 5551234,237,https://...
```

**JSON (Para APIs):**
```json
[
  {
    "titulo": "Inmobiliaria Premium",
    "correo": "contacto@inmobiliaria.com",
    ...
  }
]
```

**Excel (Formateado):**
- Columnas ajustadas automáticamente
- Formato limpio y profesional
- Listo para análisis

---

## 🔍 Herramientas Disponibles

### 1. Inspector de Selectores (`selector_inspector.py`)

Analiza la estructura real de la página:

```powershell
python selector_inspector.py
```

**Genera:**
- `inspection_report.json` - Reporte completo
- Logs detallados en consola

**Información proporcionada:**
- Todas las clases HTML encontradas
- Todos los IDs disponibles
- Atributos data-*
- Elementos por patrón

### 2. Scraper Principal (`main_fincaraiz.py`)

Script principal con capacidades completas:

```powershell
python main_fincaraiz.py
```

**Ejecuta:**
1. Inicialización de navegador
2. Detección de estructura
3. Extracción de datos
4. Guardado de resultados
5. Generación de reportes

### 3. Script Simple (`main.py`)

Versión básica sin adaptador específico:

```powershell
python main.py
```

Útil para sitios genéricos.

---

## 🛠️ Solución de Problemas

### Error: "TimeoutException: Timeout waiting for element"

**Causa:** El elemento tarda mucho en cargar

**Soluciones:**

1. Aumentar timeout en `config.py`:
```python
WAIT_TIME = 20  # aumentar a 20, 30, etc.
PAGE_LOAD_TIMEOUT = 60
```

2. Verificar conexión a Internet

3. Ejecutar con `HEADLESS = False` para ver qué sucede:
```python
HEADLESS = False  # Ver en navegador
```

---

### Error: "No se encuentran elementos de inmobiliarias"

**Causa:** La estructura HTML cambió o selectores incorrectos

**Soluciones:**

1. Ejecutar inspector:
```powershell
python selector_inspector.py
```

2. Revisar `resultados/inspection_report.json`

3. Actualizar selectores en `fincaraiz_adapter.py`:
```python
SELECTORS = {
    'container': {
        'method': 'css',
        'value': 'tu_nuevo_selector'  # Actualizar aquí
    }
}
```

---

### Error: "ModuleNotFoundError: No module named 'selenium'"

**Causa:** Dependencias no instaladas

**Solución:**
```powershell
pip install -r requirements.txt
```

---

### Error: "Chrome/Firefox not found"

**Causa:** Navegador no instalado

**Soluciones:**

1. Instalar Chrome desde: https://www.google.com/chrome/

2. O cambiar a Firefox:
```python
BROWSER_TYPE = "firefox"  # en config.py
```

3. O dejar que webdriver-manager lo instale automáticamente

---

### El script se cierra sin extraer datos

**Causa:** Error durante ejecución

**Solución:**
1. Revisar logs en `resultados/scraper.log`
2. Ejecutar con `HEADLESS = False` para ver errores visuales
3. Revisar conexión a Internet
4. Verificar que fincaraiz.com.co esté disponible

---

## 📈 Optimizaciones

### Para Velocidad

```python
# config.py
HEADLESS = True  # Más rápido
BROWSER_TYPE = "chrome"  # Más rápido que Firefox
SCROLL_PAUSE_TIME = 1  # Menos espera entre scrolls
```

### Para Confiabilidad

```python
# config.py
HEADLESS = False  # Ver lo que pasa
MAX_RETRIES = 5  # Más reintentos
IMPLICIT_WAIT = 30  # Más tiempo de espera
```

### Para Debugging

```python
# config.py
HEADLESS = False  # Ver en pantalla
OUTPUT_FORMAT = "json"  # Ver estructura
# Luego revisar: resultados/detection_report.json
```

---

## 🔐 Consideraciones Legales

⚠️ **Importante:**

1. **Términos de Servicio**: Verifica que fincaraiz.com.co permita scraping
2. **robots.txt**: Este script respeta los límites
3. **Rate Limiting**: Se incluyen pausas para no sobrecargar servidores
4. **Datos Personales**: Ten cuidado con datos de contacto

---

## 📚 Estructura del Código

### Flujo Principal

```
main_fincaraiz.py
    ↓
BrowserManager (inicializa Selenium)
    ↓
FincaraizAdapter (detecta estructura)
    ↓
AdvancedInmobiliariaExtractor (extrae datos con interacciones)
    ↓
DataSaver (guarda en CSV/JSON/Excel)
    ↓
resultados/
```

### Clase BrowserManager

Gestiona la inicialización de Selenium:
- Crea driver de Chrome/Firefox
- Configura opciones del navegador
- Establece timeouts
- Maneja el ciclo de vida

```python
from browser_manager import BrowserManager

manager = BrowserManager()
driver = manager.initialize_browser()
# ... usar driver ...
manager.close_browser()
```

### Clase FincaraizAdapter

Adaptador específico para fincaraiz:
- Detecta estructura de página
- Busca elementos usando múltiples estrategias
- Extrae datos con interacciones

```python
from fincaraiz_adapter import FincaraizAdapter

adapter = FincaraizAdapter(driver, wait)
inmobiliarias = adapter.extract_all_inmobiliarias()
```

### Clase DataSaver

Guarda datos en múltiples formatos:
- CSV
- JSON
- Excel

```python
from data_saver import DataSaver

saver = DataSaver()
filepath = saver.save_data(inmobiliarias)
summary = saver.get_summary(inmobiliarias)
```

---

## 🎓 Ejemplo Completo de Uso

```python
from browser_manager import BrowserManager
from fincaraiz_adapter import FincaraizAdapter
from data_saver import DataSaver
from config import BASE_URL
import time

# 1. Inicializar navegador
manager = BrowserManager()
driver = manager.initialize_browser()
wait = manager.get_wait()

try:
    # 2. Acceder a la página
    driver.get(BASE_URL)
    time.sleep(3)
    
    # 3. Crear adaptador
    adapter = FincaraizAdapter(driver, wait)
    
    # 4. Extraer datos
    inmobiliarias = adapter.extract_all_inmobiliarias()
    
    # 5. Guardar datos
    saver = DataSaver()
    filepath = saver.save_data(inmobiliarias)
    
    # 6. Mostrar resumen
    summary = saver.get_summary(inmobiliarias)
    print(summary)

finally:
    # 7. Cerrar navegador
    manager.close_browser()
```

---

## 💡 Consejos Útiles

1. **Primero Inspecciona**
   ```powershell
   python selector_inspector.py
   ```
   Esto te ayuda a entender la estructura.

2. **Usa Logs**
   Abre `resultados/scraper.log` para debugging

3. **Sé Paciente**
   La primera ejecución toma tiempo (carga de página, etc.)

4. **Verifica Datos**
   Abre los archivos generados en `resultados/` para verificar

5. **Automatiza**
   Usa Task Scheduler (Windows) para ejecutar automáticamente

---

## 🚀 Próximos Pasos

Después de extraer datos:

1. **Análisis en Excel**
   - Abre el CSV o XLSX en Excel
   - Crea gráficos de inmobiliarias
   - Analiza cantidad de inmuebles

2. **Integración con Base de Datos**
   - Importa datos a PostgreSQL/MySQL
   - Crea dashboards de visualización

3. **Automatización**
   - Programa ejecuciones diarias
   - Notificaciones automáticas
   - Reportes periódicos

4. **Mejoras**
   - Agregar más campos de extracción
   - Implementar caché
   - Parallelizar extracción

---

## 📞 Soporte

**Para problemas:**

1. Revisa logs en `resultados/scraper.log`
2. Ejecuta inspector: `python selector_inspector.py`
3. Verifica configuración en `config.py`
4. Revisa este documento

---

## 📝 Cambios Recientes

- ✅ Soporte para Chrome y Firefox
- ✅ Detección automática de estructura
- ✅ Múltiples formatos de salida
- ✅ Sistema de logging avanzado
- ✅ Herramienta de inspección
- ✅ Adaptador específico para fincaraiz
- ✅ Manejo de elementos interactivos

---

**¡Tu scraper está listo para usar! 🎉**

Comienza con:
```powershell
python setup_and_run.py
```

¡Éxito! 🚀
