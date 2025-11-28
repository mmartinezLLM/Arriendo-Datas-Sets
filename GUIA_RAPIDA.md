# Guía de Uso Rápido - Scraper de Inmobiliarias

## Inicio Rápido

### 1. Instalación

```powershell
# Abre PowerShell en la carpeta del proyecto y ejecuta:
python setup_and_run.py
```

O instala manualmente:

```powershell
pip install -r requirements.txt
```

### 2. Primera Ejecución (Recomendado: Inspector)

Antes de ejecutar el scraper completo, inspecciona la estructura de la página:

```powershell
python selector_inspector.py
```

Esto generará un reporte en `resultados/inspection_report.json` que te ayudará a entender la estructura.

### 3. Configurar Selectores (si es necesario)

Si el inspector detecta que la estructura es diferente, edita `fincaraiz_adapter.py`:

```python
SELECTORS = {
    'container': {
        'method': 'css',
        'value': 'TU_SELECTOR_AQUI'  # Actualiza esto
    },
    ...
}
```

### 4. Ejecutar el Scraper

```powershell
python main_fincaraiz.py
```

## Configuración

### En `config.py`:

```python
# Mostrar navegador (True) o ejecutar sin ventana (False)
HEADLESS = False

# Tipo de navegador
BROWSER_TYPE = "chrome"  # o "firefox"

# Formato de salida
OUTPUT_FORMAT = "csv"  # o "json" o "excel"

# Timeouts
WAIT_TIME = 10  # segundos
```

## Datos de Salida

Los datos se guardan en `resultados/`:

```
resultados/
├── inmobiliarias_20251112_143045.csv       # Datos en CSV
├── inmobiliarias_20251112_143045.json      # Datos en JSON
├── inmobiliarias_20251112_143045.xlsx      # Datos en Excel
├── scraper.log                             # Logs detallados
├── inspection_report.json                  # Reporte de inspección
└── detection_report.json                   # Reporte de detección
```

## Campos Extraídos

Para cada inmobiliaria se extrae:

| Campo | Descripción |
|-------|-------------|
| `titulo` | Nombre de la inmobiliaria |
| `correo` | Email de contacto |
| `telefono` | Número de teléfono (puede requerir login) |
| `cantidad_inmuebles` | Número de propiedades listadas |
| `url` | Enlace al perfil de la inmobiliaria |

## Solución de Problemas

### Problema: "No se encuentran elementos"

**Solución:**
1. Ejecuta el inspector: `python selector_inspector.py`
2. Revisa `resultados/inspection_report.json`
3. Actualiza los selectores en `fincaraiz_adapter.py`

### Problema: "Timeout esperando elementos"

**Solución:**
1. Aumenta `WAIT_TIME` en `config.py` a 15-20
2. Verifica tu conexión a Internet
3. Intenta con `HEADLESS = False` para ver qué sucede

### Problema: "ModuleNotFoundError: No module named 'selenium'"

**Solución:**
```powershell
pip install -r requirements.txt
```

### Problema: "Chrome driver no encontrado"

**Solución:**
- Se descargará automáticamente con `webdriver-manager`
- O instala Chrome manualmente desde https://www.google.com/chrome/

## Scripts Disponibles

1. **`main_fincaraiz.py`** - Scraper principal con adaptador
2. **`selector_inspector.py`** - Herramienta para inspeccionar selectores
3. **`setup_and_run.py`** - Menú interactivo
4. **`main.py`** - Versión básica (si necesitas algo simple)

## Ejemplos de Uso

### Ejecutar scraper simple:
```powershell
python main_fincaraiz.py
```

### Ejecutar y guardar en Excel:
```powershell
# Edita config.py:
OUTPUT_FORMAT = "excel"

# Luego ejecuta:
python main_fincaraiz.py
```

### Debugging con navegador visible:
```powershell
# Edita config.py:
HEADLESS = False

# Luego ejecuta:
python main_fincaraiz.py
```

## Logs

Los logs detallados se guardan en:
- **Archivo**: `resultados/scraper.log`
- **Consola**: Salida en tiempo real

Para ver solo errores:
```powershell
# En Python, modifica logger_config.py para cambiar nivel de logging
```

## Tips Importantes

1. ⏱️ **Paciencia**: El primer scrape toma tiempo (carga de página, análisis, etc.)
2. 🔄 **Reintentos**: El script reintenta automáticamente en caso de errores
3. 💾 **Backups**: Guarda tus datos extraídos regularmente
4. 📊 **Análisis**: Los datos están listos para análisis en Excel o Power BI
5. 🤖 **Automatización**: Puedes programar ejecutar el script con Task Scheduler

## Próximos Pasos

Después de extraer datos, puedes:

1. **Filtrar y limpiar datos** en Excel
2. **Analizar patrones** de inmobiliarias
3. **Integrar con CRM** para gestión de contactos
4. **Crear reportes** automáticos
5. **Exportar a base de datos** para análisis

## Soporte y Mantenimiento

- Si la página cambia, ejecuta `selector_inspector.py`
- Revisa los logs en `resultados/scraper.log`
- Los selectores se actualizan en `fincaraiz_adapter.py`

¡Éxito con tu scraper! 🚀
