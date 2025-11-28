# Guía de Procesamiento Masivo - 277,953 Inmuebles

## 📊 Resumen del Proyecto

- **Total URLs**: 277,953 inmuebles de Finca Raíz
- **División**: 10 lotes de ~27,795 URLs cada uno
- **Formato de salida**: 50 columnas (JSON + Excel)
- **Sistema de checkpoints**: Progreso guardado cada 100 URLs

---

## 🚀 Inicio Rápido

### Opción 1: Ejecutar TODOS los lotes automáticamente (recomendado)
```cmd
ejecutar_todos_lotes.bat
```
Esto procesará los 10 lotes secuencialmente. **Puede tardar varios días**.

### Opción 2: Ejecutar lotes individuales
```cmd
python procesar_lote.py 1
python procesar_lote.py 2
...
python procesar_lote.py 10
```

O usar los scripts individuales:
```cmd
resultados\lotes\ejecutar_lote_01.bat
resultados\lotes\ejecutar_lote_02.bat
...
```

---

## 📁 Estructura de Archivos

```
scraper_inmobiliarias/
├── dividir_lotes.py              # Script que divide las URLs en 10 lotes
├── procesar_lote.py              # Script que procesa un lote específico
├── ejecutar_todos_lotes.bat      # Script maestro para todos los lotes
├── resultados/
│   └── lotes/
│       ├── lote_01_urls.txt      # URLs del lote 1 (27,795 URLs)
│       ├── lote_02_urls.txt      # URLs del lote 2 (27,795 URLs)
│       ├── ...
│       ├── lote_10_urls.txt      # URLs del lote 10 (27,798 URLs)
│       ├── lote_01/              # Resultados del lote 1
│       │   ├── checkpoint_lote_01.jsonl    # Checkpoint para recuperación
│       │   ├── progreso.txt                # Progreso actual
│       │   ├── lote_01_YYYYMMDD_HHMMSS.json
│       │   └── lote_01_YYYYMMDD_HHMMSS.xlsx
│       ├── lote_02/              # Resultados del lote 2
│       └── ...
```

---

## ⚙️ Características del Sistema

### 🔄 Sistema de Checkpoints
- **Frecuencia**: Cada 100 URLs procesadas
- **Formato**: JSONL (JSON Lines) en `checkpoint_lote_XX.jsonl`
- **Recuperación automática**: Si se interrumpe, retoma desde el último checkpoint
- **Archivo de progreso**: `progreso.txt` muestra el estado actual

### 📊 Monitoreo en Tiempo Real
Cada 10 URLs muestra:
- Progreso actual (%)
- URLs exitosas vs fallidas
- Velocidad de procesamiento (URLs/seg)
- Tiempo estimado restante

### 🛡️ Robustez
- **Pausa entre requests**: 2 segundos (evita saturar el servidor)
- **Manejo de errores**: Continúa aunque fallen URLs individuales
- **Interrupciones seguras**: Ctrl+C guarda el progreso
- **Reinicio automático**: Detecta checkpoints previos

---

## 📈 Estimaciones de Tiempo

### Por Lote (~27,795 URLs)
- **Velocidad promedio**: 0.5 URLs/seg (con pausas de 2 seg)
- **Tiempo por lote**: ~15.4 horas
- **Total 10 lotes**: ~154 horas (6.4 días)

### Factores que afectan la velocidad:
- ✅ Conexión a Internet
- ✅ Carga del servidor de Finca Raíz
- ✅ Complejidad de las páginas (imágenes, datos)
- ✅ Rendimiento de tu equipo

---

## 🎯 Comandos Útiles

### Ver progreso de un lote
```cmd
type resultados\lotes\lote_01\progreso.txt
```

### Contar URLs procesadas en checkpoint
```cmd
powershell -Command "Get-Content resultados\lotes\lote_01\checkpoint_lote_01.jsonl | Measure-Object -Line"
```

### Reiniciar un lote desde cero (CUIDADO: borra el progreso)
```cmd
del resultados\lotes\lote_01\checkpoint_lote_01.jsonl
del resultados\lotes\lote_01\progreso.txt
python procesar_lote.py 1
```

### Continuar un lote interrumpido
```cmd
python procesar_lote.py 1
```
(Automáticamente detecta y carga el checkpoint)

---

## 📋 Esquema de Salida (50 columnas)

1. ID Inmos
2. Inmos
3. URL INMUEBLE
4. COD FR
5. COD FR LEGACY
6. TITULO
7. DESCRIPCION
8. PRECIO
9. PRECIO ADMIN
10. UBICACION
11. Tipo de inmueble
12. Tipo de oferta
13. Estado
14. Habitaciones
15. Baños
16. Parqueaderos
17. Estrato
18. Antigüedad
19. Metros
20. Area
21. Area privada
22. Area del terreno
23. Area lote
24. Piso No.
25. Cantidad de pisos
26. Cantidad de ambientes
27. Apto para oficina
28. Acepta permuta
29. Remodelado
30. Penthouse
31. Contrato minimo
32. Documentacion requerida
33. Acepta mascotas
34. M² de terraza
35. Comodidades
36-50. Imagen 1 a Imagen 15

---

## 🔧 Solución de Problemas

### El proceso se detiene
✅ Presiona Ctrl+C para detener de forma segura
✅ El progreso se guarda automáticamente
✅ Ejecuta el mismo comando para continuar

### Error "ChromeDriver"
```cmd
pip install --upgrade selenium
```

### Error de memoria
- Procesa lotes individuales en lugar de todos juntos
- Reinicia el equipo entre lotes

### URLs que fallan constantemente
- Son normales, se registran como "fallidas"
- El proceso continúa con las siguientes URLs
- Revisa los logs para ver detalles

---

## 📊 Consolidación de Resultados (Opcional)

Una vez completados todos los lotes, puedes consolidarlos:

```python
import pandas as pd
import glob

# Leer todos los Excel de lotes
archivos = glob.glob('resultados/lotes/lote_*/lote_*.xlsx')
dfs = [pd.read_excel(f) for f in archivos]

# Consolidar
df_total = pd.concat(dfs, ignore_index=True)

# Guardar
df_total.to_excel('resultados/TODOS_INMUEBLES_CONSOLIDADO.xlsx', index=False)
print(f"Total propiedades: {len(df_total):,}")
```

---

## ⚠️ Recomendaciones

1. **Ejecución nocturna**: Deja correr durante la noche/fin de semana
2. **No apagar el PC**: Configura para que no entre en suspensión
3. **Monitorea el primer lote**: Verifica que todo funcione bien
4. **Backups periódicos**: Copia la carpeta `resultados/lotes/` regularmente
5. **Espacio en disco**: Asegúrate de tener al menos 10 GB libres

---

## 📞 Soporte

Si encuentras problemas:
1. Revisa el archivo `progreso.txt` del lote
2. Verifica los logs en la consola
3. Asegúrate de tener conexión a Internet estable
4. Verifica que el archivo `Inmuebles.xlsx` existe y tiene las URLs

---

## ✅ Checklist antes de iniciar

- [ ] Archivo `Inmuebles.xlsx` existe y tiene 277,953 URLs
- [ ] Python 3.x instalado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] ChromeDriver compatible con tu versión de Chrome
- [ ] Conexión a Internet estable
- [ ] Al menos 10 GB de espacio libre
- [ ] PC configurado para no entrar en suspensión

---

**¡Listo para procesar 277,953 inmuebles!** 🚀
