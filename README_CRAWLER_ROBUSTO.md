# Sistema Robusto de Crawling para 300k+ Inmuebles

## Características principales

### 1. **Checkpoints incrementales**
- Guarda progreso cada N URLs (configurable)
- Reanudar automáticamente sin repetir trabajo
- Archivo `checkpoint_TIMESTAMP.json` con estado completo

### 2. **Reintentos automáticos**
- Backoff exponencial (2^intento segundos)
- Configurable: 3 intentos por defecto
- Log detallado de cada reintento

### 3. **Paralelización controlada**
- ThreadPoolExecutor con límite de workers
- Procesamiento por batches para controlar memoria
- Cada thread tiene su propio driver de Selenium

### 4. **Integridad de datos**
- Detección de duplicados por URL
- Validación antes de guardar
- Formato JSONL (append-only) evita corrupción
- Consolidación final a JSON único

### 5. **Logging completo**
- Archivo `.log` con timestamps
- Métricas: tasa de éxito, velocidad, errores
- Archivo `.jsonl` separado para errores

### 6. **Optimizaciones de memoria**
- Procesamiento por batches
- Drivers se crean/destruyen por batch
- Desactivación de recursos pesados (imágenes, CSS, etc.)

## Uso básico

```python
from property_crawler_robust import crawl_properties_robust

# Lista de URLs a procesar
urls = [...]  # Hasta 300k+ URLs

# Configuración personalizada (opcional)
config = {
    'checkpoint_interval': 10,  # Guardar cada 10 URLs
    'max_retries': 3,           # Reintentos por URL
    'batch_size': 100,          # URLs por batch
    'max_workers': 4,           # Threads concurrentes
    'request_delay': 0.5,       # Pausa entre requests (seg)
    'headless': True,           # Modo headless
    'page_timeout': 20,         # Timeout por página (seg)
}

# Ejecutar crawling
stats = crawl_properties_robust(urls, output_dir='resultados', config=config)

print(f"Procesadas: {stats['success']}")
print(f"Fallidas: {stats['failed']}")
print(f"Tasa: {stats['rate_per_second']:.2f} props/seg")
```

## Archivos generados

- `properties_TIMESTAMP.jsonl`: Resultados en tiempo real (línea por línea)
- `properties_TIMESTAMP_consolidated.json`: JSON final consolidado
- `checkpoint_TIMESTAMP.json`: Estado para reanudar
- `errors_TIMESTAMP.jsonl`: URLs fallidas con detalles
- `crawler_TIMESTAMP.log`: Log completo de ejecución

## Reanudar una sesión interrumpida

```python
# El crawler detecta automáticamente el checkpoint más reciente
# Solo ejecuta nuevamente con las mismas URLs:
stats = crawl_properties_robust(urls)
# Saltará las URLs ya procesadas
```

## Configuración para 300k inmuebles

### Opción 1: Máxima velocidad (servidor potente)
```python
config_produccion = {
    'checkpoint_interval': 50,
    'batch_size': 500,
    'max_workers': 8,       # 8 threads paralelos
    'request_delay': 0.3,
    'headless': True,
    'page_timeout': 15,
}
# Tiempo estimado: ~20-30 horas
```

### Opción 2: Equilibrada (equipo normal)
```python
config_equilibrada = {
    'checkpoint_interval': 20,
    'batch_size': 200,
    'max_workers': 4,       # 4 threads paralelos
    'request_delay': 0.5,
    'headless': True,
    'page_timeout': 20,
}
# Tiempo estimado: ~40-50 horas
```

### Opción 3: Conservadora (recursos limitados)
```python
config_conservadora = {
    'checkpoint_interval': 10,
    'batch_size': 50,
    'max_workers': 2,       # 2 threads paralelos
    'request_delay': 1.0,
    'headless': True,
    'page_timeout': 25,
}
# Tiempo estimado: ~80-100 horas
```

## Monitoreo en tiempo real

### Ver progreso durante la ejecución
```powershell
# Ver últimas líneas del log
Get-Content resultados\crawler_*.log -Tail 20 -Wait

# Contar URLs procesadas
(Get-Content resultados\properties_*.jsonl).Count

# Contar errores
(Get-Content resultados\errors_*.jsonl).Count
```

## Generación de Excel final

```python
# Una vez completado el crawling
from json_to_excel_properties import json_to_excel

json_to_excel(
    'resultados/properties_TIMESTAMP_consolidated.json',
    'resultados/properties_final.xlsx'
)
```

## Estimaciones de rendimiento

| Configuración | Threads | URLs/seg | 300k inmuebles |
|--------------|---------|----------|----------------|
| Máxima       | 8       | ~2.5     | 33 horas       |
| Equilibrada  | 4       | ~1.8     | 46 horas       |
| Conservadora | 2       | ~1.0     | 83 horas       |

**Nota**: Tiempos reales dependen de conexión a internet, latencia del sitio y recursos del sistema.

## Troubleshooting

### Error: "Chrome driver not found"
```powershell
pip install --upgrade selenium
# Asegurar que chromedriver esté en PATH
```

### Error: "Memory error"
```python
# Reducir batch_size y max_workers
config = {'batch_size': 50, 'max_workers': 2}
```

### Crawling muy lento
```python
# Aumentar workers y reducir delays
config = {'max_workers': 6, 'request_delay': 0.2}
```

### Muchos errores (>10%)
```python
# Aumentar timeouts y reintentos
config = {
    'page_timeout': 30,
    'max_retries': 5,
    'retry_delay_base': 3
}
```

## Mejores prácticas

1. **Empezar con prueba pequeña**: 100-1000 URLs para ajustar configuración
2. **Monitorear primeras horas**: Verificar tasa de éxito y ajustar
3. **Ejecutar en horario valle**: Menos tráfico = mejor rendimiento
4. **Usar servidor dedicado**: Para volúmenes masivos
5. **Backup periódico**: Copiar checkpoints cada 6-12 horas
6. **Revisar logs de errores**: Identificar patrones de fallo

## Contacto y soporte

Para problemas o dudas, revisar:
- Archivos de log en `resultados/`
- Checkpoint JSON para ver estado exacto
- Errors JSONL para URLs problemáticas
