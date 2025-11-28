# 🌐 Scraper de Inmobiliarias - FinCaRaíz Colombia

**Sistema automatizado para extraer información de inmobiliarias desde fincaraiz.com.co**

---

## 🚀 Inicio Rápido (Windows)

### Opción 1: Instalador Automático (Recomendado)

Simplemente **haz doble clic** en:
```
instalar.bat
```

Luego selecciona qué deseas hacer.

### Opción 2: PowerShell

```powershell
# 1. Abrir PowerShell en la carpeta del proyecto
# 2. Ejecutar instalación
pip install -r requirements.txt

# 3. Ejecutar scraper
python main_fincaraiz.py
```

### Opción 3: Menú Interactivo (Python)

```powershell
python setup_and_run.py
```

---

## 📊 ¿Qué Extrae?

Para cada inmobiliaria obtiene:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **Título** | Nombre de la inmobiliaria | "Inmobiliaria Premium S.A.S" |
| **Correo** | Email de contacto | "contacto@inmobiliaria.com" |
| **Teléfono** | Número telefónico | "+57 1 5551234" |
| **Inmuebles** | Cantidad de propiedades | 237 |
| **URL** | Link al perfil | "https://fincaraiz.com.co/..." |

---

## 📁 Archivos del Proyecto

```
scraper_inmobiliarias/
├── 📄 README.md                    ← Este archivo
├── 📄 DOCUMENTACION_COMPLETA.md    ← Documentación detallada
├── 📄 GUIA_RAPIDA.md               ← Guía de uso
│
├── 🚀 Scripts para Ejecutar
│   ├── instalar.bat                ← Instalador automático (Windows)
│   ├── ejecutar_scraper.bat        ← Ejecutar scraper (Windows)
│   ├── ejecutar_inspector.bat      ← Ejecutar inspector (Windows)
│   ├── main_fincaraiz.py           ← Script principal (Python)
│   ├── selector_inspector.py       ← Inspector de estructura
│   └── setup_and_run.py            ← Menú interactivo
│
├── ⚙️ Módulos de Código
│   ├── config.py
│   ├── browser_manager.py
│   ├── extractor.py
│   ├── advanced_extractor.py
│   ├── fincaraiz_adapter.py
│   ├── data_saver.py
│   └── logger_config.py
│
├── 📦 Configuración
│   ├── requirements.txt
│   └── .env.example
│
└── 📁 resultados/                  (Se crea automáticamente)
    ├── inmobiliarias_*.csv
    ├── inmobiliarias_*.json
    ├── inmobiliarias_*.xlsx
    ├── scraper.log
    └── *.json (reportes de inspección)
```

---

## ⚡ Primeros Pasos

### 1️⃣ Instalar Dependencias

**Windows (Más fácil):**
```
Haz doble clic en: instalar.bat
```

**O en PowerShell:**
```powershell
pip install -r requirements.txt
```

### 2️⃣ Inspeccionar la Estructura (Opcional pero Recomendado)

Esto te ayuda a entender cómo extrae los datos:

**Windows:**
```
Haz doble clic en: ejecutar_inspector.bat
```

**O en PowerShell:**
```powershell
python selector_inspector.py
```

### 3️⃣ Ejecutar el Scraper

**Windows:**
```
Haz doble clic en: ejecutar_scraper.bat
```

**O en PowerShell:**
```powershell
python main_fincaraiz.py
```

### 4️⃣ Ver Resultados

Abre la carpeta `resultados/` para ver:
- 📊 Datos en CSV, JSON o Excel
- 📝 Logs detallados
- 📋 Reportes de inspección

---

## ⚙️ Configuración

Edita `config.py` para personalizar:

```python
# Mostrar navegador (True/False)
HEADLESS = False

# Tipo de navegador
BROWSER_TYPE = "chrome"  # o "firefox"

# Formato de salida
OUTPUT_FORMAT = "csv"  # "csv", "json" o "excel"

# Tiempo de espera (segundos)
WAIT_TIME = 10
```

---

## 📋 Datos de Salida

### Formato CSV (Excel)

```csv
titulo,correo,telefono,cantidad_inmuebles,url
"Inmobiliaria Premium","contacto@inmobiliaria.com","+57 1 5551234",237,"https://..."
```

### Formato JSON

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

### Formato Excel

Archivo `.xlsx` con:
- Columnas formateadas automáticamente
- Datos listos para análisis
- Compatible con Power BI

---

## 🔍 Solución de Problemas

### ❌ "No se encuentran elementos"

**Solución:**
```powershell
# Ejecutar inspector
python selector_inspector.py

# Revisar: resultados/inspection_report.json
# Actualizar selectores en: fincaraiz_adapter.py
```

### ❌ "Timeout esperando elementos"

**Solución:**
```python
# En config.py, aumentar:
WAIT_TIME = 20  # o mayor
PAGE_LOAD_TIMEOUT = 50
```

### ❌ "ModuleNotFoundError"

**Solución:**
```powershell
pip install -r requirements.txt
```

### ❌ "Chrome/Firefox no encontrado"

**Solución:**
1. Instalar Chrome desde: https://www.google.com/chrome/
2. O cambiar a Firefox en `config.py`
3. webdriver-manager lo instalará automáticamente

---

## 📚 Documentación Completa

Para información detallada, revisa:

- **`DOCUMENTACION_COMPLETA.md`** - Guía exhaustiva con ejemplos
- **`GUIA_RAPIDA.md`** - Referencia rápida de comandos

---

## 🎓 Ejemplo de Uso

### Script Simple

```python
from main_fincaraiz import main
main()
```

### Script Personalizado

```python
from browser_manager import BrowserManager
from fincaraiz_adapter import FincaraizAdapter
from data_saver import DataSaver

# Inicializar
manager = BrowserManager()
driver = manager.initialize_browser()
wait = manager.get_wait()

# Acceder y extraer
driver.get("https://www.fincaraiz.com.co/inmobiliarias/")
adapter = FincaraizAdapter(driver, wait)
inmobiliarias = adapter.extract_all_inmobiliarias()

# Guardar
saver = DataSaver()
saver.save_data(inmobiliarias)

# Limpiar
manager.close_browser()
```

---

## 💡 Consejos

✅ **Para Debugging:**
```python
# En config.py
HEADLESS = False  # Ver navegador
OUTPUT_FORMAT = "json"  # Ver estructura fácilmente
```

✅ **Para Velocidad:**
```python
# En config.py
HEADLESS = True  # Sin interfaz gráfica
SCROLL_PAUSE_TIME = 1  # Menos esperas
```

✅ **Para Confiabilidad:**
```python
# En config.py
MAX_RETRIES = 5
IMPLICIT_WAIT = 20
```

---

## 🔐 Notas Legales

⚠️ Asegúrate de:
- ✅ Verificar términos de servicio de fincaraiz.com.co
- ✅ Respetar robots.txt
- ✅ No sobrecargar servidores (el script incluye pausas)
- ✅ Usar datos con responsabilidad

---

## 🚀 Casos de Uso

1. **Análisis de Mercado**
   - Cantidad de inmobiliarias activas
   - Distribución de propiedades

2. **Lead Generation**
   - Recolectar emails de contacto
   - Números telefónicos de inmobiliarias

3. **Investigación**
   - Tendencias del sector inmobiliario
   - Competencia y análisis de mercado

4. **Integración**
   - Exportar a CRM
   - Importar a base de datos
   - Crear dashboards

---

## 📦 Dependencias

- **selenium** - Automatización de navegador
- **beautifulsoup4** - Análisis HTML
- **pandas** - Manipulación de datos
- **webdriver-manager** - Gestión automática de drivers
- **requests** - Cliente HTTP

Se instalan automáticamente con:
```powershell
pip install -r requirements.txt
```

---

## ✨ Características

✅ Extracción automatizada de datos
✅ Navegador automatizado (Chrome/Firefox)
✅ Detección inteligente de estructura
✅ Múltiples formatos de salida (CSV, JSON, Excel)
✅ Logging detallado
✅ Herramienta de inspección de selectores
✅ Manejo de elementos interactivos
✅ Totalmente configurable
✅ Fácil de usar en Windows

---

## 📞 Soporte

**Si algo no funciona:**

1. Revisa logs en `resultados/scraper.log`
2. Lee `DOCUMENTACION_COMPLETA.md`
3. Ejecuta inspector: `python selector_inspector.py`
4. Verifica configuración en `config.py`

---

## 🎉 ¡Listo!

Ahora puedes:

1. **Haz doble clic en `instalar.bat`** para empezar
2. Selecciona "Ejecutar scraper"
3. ¡Espera a que se complete!

Los datos estarán listos en `resultados/`

---

**Desarrollado para BROWSER TRAVEL SOLUTIONS S.A.S VIAJEMOS**

**Versión:** 1.0  
**Última actualización:** Noviembre 2025

---

### 🔗 Recursos Útiles

- [Selenium Documentation](https://www.selenium.dev/)
- [BeautifulSoup4 Documentation](https://www.crummy.com/software/BeautifulSoup/)
- [Pandas Documentation](https://pandas.pydata.org/)
- [Python Official](https://www.python.org/)

---

¡Éxito con tu scraper! 🚀
