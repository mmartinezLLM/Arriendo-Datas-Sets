# 📦 INVENTARIO COMPLETO DEL PROYECTO

## 🎯 Resumen Ejecutivo

Se ha creado un **Sistema Completo de Web Scraping y Crawling** para extraer información de inmobiliarias desde fincaraiz.com.co. El sistema es:

- ✅ **Totalmente Automático** - Funciona sin intervención
- ✅ **Fácil de Usar** - Menús interactivos en Windows
- ✅ **Profesional** - Código bien documentado y organizado
- ✅ **Confiable** - Manejo robusto de errores
- ✅ **Flexible** - Múltiples formatos de salida
- ✅ **Extensible** - Fácil de personalizar

---

## 📁 ARCHIVOS CREADOS

### 🚀 SCRIPTS EJECUTABLES (Lo que usarás)

```
instalar.bat
├─ Instalador automático para Windows
├─ Descarga todas las dependencias
├─ Menú interactivo para elegir operación
└─ Requiere: Estar en PowerShell/CMD

ejecutar_scraper.bat
├─ Ejecuta el scraper con un clic
├─ Abre navegador y extrae datos
└─ Guarda resultados automáticamente

ejecutar_inspector.bat
├─ Herramienta de inspección de estructura
├─ Útil para debugging cuando la página cambia
└─ Genera reportes detallados

main_fincaraiz.py
├─ Script principal (RECOMENDADO)
├─ Scraper especializado para fincaraiz.com.co
├─ Ejecutar: python main_fincaraiz.py
└─ Extrae todas las inmobiliarias y sus datos

main.py
├─ Versión básica del scraper
├─ Para sitios genéricos
└─ Menos especializado que main_fincaraiz.py

selector_inspector.py
├─ Inspecciona estructura de la página
├─ Genera reporte JSON
├─ Útil cuando cambia la estructura
└─ Ejecutar: python selector_inspector.py

setup_and_run.py
├─ Menú interactivo en Python
├─ Interfaz alternativa a los .bat
├─ Ejecutar: python setup_and_run.py
└─ Bueno para macOS/Linux también

selector_manager.py
├─ Gestiona los selectores CSS/XPath
├─ Permite actualizar selectores fácilmente
├─ Exporta/importa configuraciones
└─ Ejecutar: python selector_manager.py
```

---

### ⚙️ MÓDULOS DE CÓDIGO (Núcleo del sistema)

```
config.py
├─ Configuración global del proyecto
├─ Parámetros de Selenium
├─ URLs y timeouts
├─ Formatos de salida
└─ Editar aquí para personalizar

logger_config.py
├─ Sistema de logging
├─ Guarda logs en archivo y consola
├─ Niveles de detalle configurable
└─ Archivo: resultados/scraper.log

browser_manager.py
├─ Gestor de Selenium
├─ Inicializa navegadores (Chrome/Firefox)
├─ Configura opciones y timeouts
├─ Maneja el ciclo de vida del navegador
└─ Clase: BrowserManager

extractor.py
├─ Extractor básico de datos
├─ Métodos para extraer campos
├─ Scroll automático de página
└─ Clase: InmobiliariaExtractor

advanced_extractor.py
├─ Extractor avanzado con interacciones
├─ Manejo de elementos interactivos
├─ ActionChains para interacciones complejas
├─ Reintentos automáticos
└─ Clase: AdvancedInmobiliariaExtractor

fincaraiz_adapter.py
├─ Adaptador especializado para fincaraiz.com.co
├─ Detecta estructura de la página automáticamente
├─ Múltiples estrategias de búsqueda
├─ Selectores específicos del sitio
└─ Clase: FincaraizAdapter

data_saver.py
├─ Guardador de datos
├─ Soporta: CSV, JSON, Excel
├─ Formatos automáticamente
├─ Genera resúmenes
└─ Clase: DataSaver

selector_manager.py
├─ Gestor de selectores
├─ Almacena selectores en JSON
├─ Importa/exporta configuraciones
└─ Clase: SelectorManager
```

---

### 📚 DOCUMENTACIÓN (Lee esto primero!)

```
COMIENZA_AQUI.txt
├─ ⭐ ARCHIVO MÁS IMPORTANTE
├─ Instrucciones paso a paso
├─ Preguntas frecuentes
├─ Solución rápida de problemas
└─ Tiempo estimado de ejecución

LEEME.md
├─ Resumen ejecutivo en Markdown
├─ Inicio rápido en 3 pasos
├─ Estructura del proyecto
├─ Datos de salida
└─ Casos de uso

README.md
├─ Documentación técnica completa
├─ Funcionalidades detalladas
├─ Estructura del proyecto
├─ Requisitos y instalación
└─ Archivos de log

GUIA_RAPIDA.md
├─ Referencia rápida de comandos
├─ Configuración común
├─ Ejemplos de uso
└─ Tips importantes

DOCUMENTACION_COMPLETA.md
├─ Guía exhaustiva
├─ Ejemplos de código
├─ Clases y métodos
├─ Solución detallada de problemas
└─ Optimizaciones

INVENTARIO_DEL_PROYECTO.md
├─ Este archivo
├─ Lista de todos los archivos
├─ Descripción de cada componente
└─ Cómo están organizados
```

---

### 📦 CONFIGURACIÓN

```
requirements.txt
├─ Dependencias de Python
├─ Versiones específicas
├─ Instalar: pip install -r requirements.txt
└─ Contiene: selenium, beautifulsoup4, pandas, etc.

.env.example
├─ Variables de entorno de ejemplo
├─ Configuración opcional
└─ Copiar a .env y editar si necesario

config.py
├─ Configuración global
├─ Parámetros personalizables
├─ Timeouts y opciones
└─ Editar según necesidades
```

---

### 📁 CARPETAS GENERADAS (Automáticas)

```
resultados/
├─ Se crea automáticamente
├─ Archivos de salida:
│  ├─ inmobiliarias_20251112_143045.csv
│  ├─ inmobiliarias_20251112_143045.json
│  ├─ inmobiliarias_20251112_143045.xlsx
│  ├─ scraper.log (logs detallados)
│  ├─ inspection_report.json
│  ├─ detection_report.json
│  └─ selectors_config.json (si existe)
```

---

## 🚀 CÓMO USARLO

### Para Usuarios Windows (Recomendado)

1. **Abre la carpeta del proyecto**
2. **Haz DOBLE CLIC en `instalar.bat`**
3. **Selecciona opción 2** (Ejecutar scraper)
4. **¡Espera a que termine!**
5. **Ve a la carpeta `resultados/` para ver tus datos**

### Para Desarrolladores Python

```powershell
# Opción 1: Menú interactivo
python setup_and_run.py

# Opción 2: Scraper directo
python main_fincaraiz.py

# Opción 3: Inspector
python selector_inspector.py

# Opción 4: Gestor de selectores
python selector_manager.py
```

---

## 📊 FLUJO DE DATOS

```
Usuario inicia instalar.bat
           ↓
   ¿Instalar dependencias?
           ↓
   ¿Qué hacer? (1-4)
           ↓
    Opción 2: Ejecutar Scraper
           ↓
   BrowserManager inicializa Selenium
           ↓
   Abre https://www.fincaraiz.com.co/inmobiliarias/
           ↓
   FincaraizAdapter detecta estructura
           ↓
   AdvancedInmobiliariaExtractor extrae datos
           ↓
   DataSaver guarda en CSV/JSON/Excel
           ↓
   ✓ Datos listos en resultados/
           ↓
   Usuario abre resultados/ y ve sus datos
```

---

## 🔄 CICLO DE VIDA DEL PROGRAMA

```
INICIO
  ↓
Cargar Configuración (config.py)
  ↓
Inicializar Logging (logger_config.py)
  ↓
Inicializar Navegador (browser_manager.py)
  ↓
Acceder a URL de fincaraiz
  ↓
Detectar Estructura (fincaraiz_adapter.py)
  ↓
Extraer Datos (advanced_extractor.py)
  ├─ Scroll de página
  ├─ Buscar elementos
  ├─ Interactuar con botones
  ├─ Extraer información
  └─ Guardar en lista
  ↓
Procesar Todos los Elementos
  ↓
Guardar Datos (data_saver.py)
  ├─ CSV
  ├─ JSON
  └─ Excel
  ↓
Generar Resumen
  ↓
Cerrar Navegador
  ↓
FIN
```

---

## 🎯 DATOS EXTRAÍDOS

### Por cada inmobiliaria obtiene:

| Campo | Tipo | Ejemplo |
|-------|------|---------|
| `titulo` | string | "Inmobiliaria Premium S.A.S" |
| `correo` | string | "contacto@inmobiliaria.com" |
| `telefono` | string | "+57 1 5551234" |
| `cantidad_inmuebles` | int | 237 |
| `url` | string | "https://fincaraiz.com.co/..." |

### Formatos de salida:

- **CSV** - Para Excel/Sheets
- **JSON** - Para APIs/JavaScript
- **XLSX** - Excel formateado

---

## ⚙️ CONFIGURACIONES COMUNES

### Ver el navegador abierto:
```python
# En config.py
HEADLESS = False
```

### Aumentar tiempo de espera:
```python
# En config.py
WAIT_TIME = 20
PAGE_LOAD_TIMEOUT = 50
```

### Cambiar formato de salida:
```python
# En config.py
OUTPUT_FORMAT = "excel"  # "csv", "json" o "excel"
```

### Usar Firefox:
```python
# En config.py
BROWSER_TYPE = "firefox"
```

---

## 🔍 DEBUGGING

### Ver estructura de página:
```powershell
python selector_inspector.py
# Genera: resultados/inspection_report.json
```

### Actualizar selectores:
```powershell
python selector_manager.py
# Menú para actualizar selectores
```

### Ver logs detallados:
```powershell
# Archivo: resultados/scraper.log
# O ejecutar con HEADLESS=False
```

---

## 📈 ESTADÍSTICAS TÍPICAS

Después de ejecutar, esperarás ver:

- **Total de inmobiliarias**: 50-200+
- **Tiempo de ejecución**: 5-15 minutos
- **Tamaño del archivo CSV**: 50-500 KB
- **Archivos generados**: 3-4 (CSV, JSON, XLSX, logs)

---

## ✨ CARACTERÍSTICAS

✅ Extracción automatizada
✅ Navegador con Chrome/Firefox
✅ Detección automática de estructura
✅ Múltiples formatos de salida
✅ Logging detallado
✅ Manejo de interacciones
✅ Reintentos automáticos
✅ Interfaz amigable Windows
✅ Documentación completa
✅ Código modular y extensible

---

## 🛠️ DEPENDENCIAS INSTALADAS

Cuando ejecutas `instalar.bat`, se instalan:

- `selenium==4.15.2` - Automatización de navegador
- `beautifulsoup4==4.12.2` - Análisis HTML
- `requests==2.31.0` - Cliente HTTP
- `pandas==2.1.3` - Manipulación de datos
- `webdriver-manager==4.0.1` - Gestión de drivers
- `lxml==4.9.3` - Procesamiento XML/HTML
- `python-dotenv==1.0.0` - Variables de entorno

---

## 📞 SOPORTE

Si algo no funciona:

1. Abre `COMIENZA_AQUI.txt`
2. Lee `DOCUMENTACION_COMPLETA.md`
3. Revisa logs en `resultados/scraper.log`
4. Ejecuta `python selector_inspector.py`
5. Verifica configuración en `config.py`

---

## 🎯 PRÓXIMOS PASOS

1. **Lee** `COMIENZA_AQUI.txt`
2. **Ejecuta** `instalar.bat`
3. **Selecciona** opción 2 (Scraper)
4. **Espera** a que termine
5. **Abre** resultados/ para ver datos
6. **Analiza** en Excel o donde prefieras

---

## 📝 EJEMPLO DE SALIDA

### CSV (resultados/inmobiliarias_*.csv):
```csv
titulo,correo,telefono,cantidad_inmuebles,url
"Inmobiliaria Premium","contacto@inmobiliaria.com","+57 1 5551234",237,"https://..."
"Inmobiliaria Elite","info@elite.com","Requiere inicio sesión",156,"https://..."
```

### JSON (resultados/inmobiliarias_*.json):
```json
[
  {
    "titulo": "Inmobiliaria Premium",
    "correo": "contacto@inmobiliaria.com",
    "telefono": "+57 1 5551234",
    "cantidad_inmuebles": 237,
    "url": "https://..."
  }
]
```

---

## ✅ CHECKLIST DE INICIO

- [ ] Leer `COMIENZA_AQUI.txt`
- [ ] Ejecutar `instalar.bat`
- [ ] Ver que se instalan dependencias
- [ ] Seleccionar opción 2
- [ ] Esperar a que termine
- [ ] Abrir carpeta `resultados/`
- [ ] Abrir archivo CSV en Excel
- [ ] ¡Analizar datos! 🎉

---

## 🎉 ¡LISTO PARA COMENZAR!

**Próximo paso:** Abre y lee `COMIENZA_AQUI.txt`

Luego ejecuta `instalar.bat` y disfruta de tus datos! 🚀

---

**Versión:** 1.0  
**Fecha:** Noviembre 2025  
**Desarrollado por:** BROWSER TRAVEL SOLUTIONS S.A.S VIAJEMOS

---
