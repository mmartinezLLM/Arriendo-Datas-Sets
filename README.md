# Scraper de Inmobiliarias - FinCaRaíz Colombia

Sistema automatizado para extraer información de inmobiliarias del sitio fincaraiz.com.co

## Funcionalidades

- 🌐 Web scraping con navegador automatizado (Selenium)
- 📊 Extracción de información de inmobiliarias:
  - Título/Nombre
  - Correo electrónico
  - Número de teléfono
  - Cantidad de inmuebles
  - URL de perfil
- 💾 Guardado en múltiples formatos (CSV, JSON, Excel)
- 📝 Logging detallado de operaciones
- ⚙️ Configuración flexible y personalizable

## Requisitos Previos

- Python 3.8+
- Windows (se puede adaptar a otros SO)
- Conexión a Internet
- Navegador Chrome o Firefox instalado

## Instalación

### 1. Clonar o descargar el proyecto

```bash
cd scraper_inmobiliarias
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar el archivo .env (opcional)

```bash
copy .env.example .env
```

## Configuración

Edita el archivo `config.py` para personalizar:

```python
# Tipo de navegador
BROWSER_TYPE = "chrome"  # 'chrome' o 'firefox'

# Modo headless (sin interfaz gráfica)
HEADLESS = False  # Cambiar a True para ejecutar sin ventana del navegador

# Timeouts
IMPLICIT_WAIT = 10
PAGE_LOAD_TIMEOUT = 30

# Formato de salida
OUTPUT_FORMAT = "csv"  # 'csv', 'json', 'excel'
```

## Uso

### Ejecución Básica

```bash
python main.py
```

### Ejecución en Background

```bash
python main.py &  # Linux/Mac
start python main.py  # Windows
```

## Estructura del Proyecto

```
scraper_inmobiliarias/
├── main.py                 # Script principal
├── config.py              # Configuración del proyecto
├── browser_manager.py     # Gestor de Selenium
├── extractor.py           # Lógica de extracción de datos
├── data_saver.py          # Guardado de datos
├── logger_config.py       # Configuración de logging
├── requirements.txt       # Dependencias de Python
├── .env.example           # Variables de entorno ejemplo
├── README.md              # Este archivo
└── resultados/            # Carpeta de salida (se crea automáticamente)
    ├── inmobiliarias_YYYYMMDD_HHMMSS.csv
    ├── inmobiliarias_YYYYMMDD_HHMMSS.json
    ├── inmobiliarias_YYYYMMDD_HHMMSS.xlsx
    └── scraper.log
```

## Salida de Datos

### Estructura de Datos Extraídos

Cada inmobiliaria contiene:

```json
{
  "titulo": "Nombre de la Inmobiliaria",
  "correo": "contacto@inmobiliaria.com",
  "telefono": "+57 1 1234567 o 'Requiere inicio de sesión'",
  "cantidad_inmuebles": 245,
  "url": "https://www.fincaraiz.com.co/inmobiliarias/nombre-inmobiliaria"
}
```

### Formatos de Salida

- **CSV**: Ideal para análisis en Excel o importar a bases de datos
- **JSON**: Estructurado para integración con APIs o aplicaciones web
- **Excel**: Con formato automático y ajuste de columnas

## Archivos de Log

Los logs se guardan en `resultados/scraper.log` con información detallada:

```
12/11/2025 14:30:45 - __main__ - INFO - INICIANDO SCRAPER DE INMOBILIARIAS
12/11/2025 14:30:46 - __main__ - INFO - Navegador chrome inicializado exitosamente
12/11/2025 14:30:48 - __main__ - INFO - Accediendo a https://www.fincaraiz.com.co/inmobiliarias/...
...
```

## Solución de Problemas

### Error: "Chrome driver no encontrado"

- Se descargará automáticamente con `webdriver-manager`
- Si persiste, instala Chrome manualmente

### Error: "Timeout esperando elementos"

- Aumenta `WAIT_TIME` en config.py
- Verifica tu conexión a Internet
- La estructura HTML del sitio puede haber cambiado

### Error: "No se encuentran elementos de inmobiliarias"

- La estructura HTML del sitio puede haber cambiado
- Verifica los selectores en `extractor.py`
- Revisa el archivo de log para más detalles

### El script se cierra sin datos

- Revisa los logs en `resultados/scraper.log`
- Verifica la conectividad a fincaraiz.com.co
- Intenta con `HEADLESS = False` para ver qué sucede

## Mejoras Futuras

- [ ] Scraping de información detallada de cada inmobiliaria
- [ ] Manejo de captchas
- [ ] Integración con bases de datos
- [ ] Planificación automática de ejecuciones
- [ ] API REST para acceder a los datos
- [ ] Dashboard de visualización
- [ ] Sistema de notificaciones
- [ ] Caché de datos para no duplicar

## Notas Importantes

1. **Respeto a robots.txt**: Este script respeta los límites de scraping del sitio
2. **Términos de Servicio**: Verifica que el scraping esté permitido
3. **Throttling**: Se incluyen pausas entre requests para no sobrecargar el servidor
4. **User-Agent**: Se simula un navegador real

## Limitaciones Conocidas

- El teléfono puede requerir inicio de sesión en el sitio original
- Algunos datos pueden no estar disponibles para todas las inmobiliarias
- La estructura HTML puede cambiar sin previo aviso

## Contribución

Para reportar problemas o sugerencias, abre un issue o contacta al administrador.

## Licencia

Este proyecto es para uso educativo y de investigación.

## Autor

Desarrollado para BROWSER TRAVEL SOLUTIONS S.A.S VIAJEMOS

## Soporte

Para soporte técnico, revisa los logs y la documentación anterior.
