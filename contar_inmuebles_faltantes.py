import os
import pandas as pd
from pathlib import Path
from glob import glob

# Rutas de los lotes
base_dir = Path(r"C:/Users/Miguel Martinez SSD/OneDrive - BROWSER TRAVEL SOLUTIONS S.A.S VIAJEMOS/Documentos/PROYECTOS/ARRIENDO DATA SETS/InmueblesFR")
lote_dirs = [base_dir / f"lote_{i:02d}" for i in range(1, 6)]

# Leer todas las URLs originales de los excels de lote
urls_totales = set()
for i, lote_dir in enumerate(lote_dirs, 1):
    excel_path = lote_dir / f"inmuebles_lote_{i:02d}.xlsx"
    if not excel_path.exists():
        continue
    df = pd.read_excel(excel_path)
    if 'URL' in df.columns:
        urls = df['URL'].dropna().tolist()
        urls_totales.update(urls)

# Leer las URLs ya procesadas
urls_procesadas = set()
for lote_dir in lote_dirs:
    backups = sorted(glob(str(lote_dir / f"lote_*_backup_*.json")))
    if not backups:
        continue
    backups.sort(key=lambda x: int(x.split('_backup_')[1].split('_')[0]), reverse=True)
    latest_backup = backups[0]
    import json
    with open(latest_backup, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            for d in data:
                url = d.get('url_inmueble')
                if url:
                    urls_procesadas.add(url)
        except Exception as e:
            print(f"Error leyendo {latest_backup}: {e}")


# Mostrar faltantes por lote
for i, lote_dir in enumerate(lote_dirs, 1):
    excel_path = lote_dir / f"inmuebles_lote_{i:02d}.xlsx"
    if not excel_path.exists():
        print(f"Lote {i}: archivo no encontrado")
        continue
    df = pd.read_excel(excel_path)
    if 'URL' in df.columns:
        urls_lote = set(df['URL'].dropna().tolist())
        faltan_lote = urls_lote - urls_procesadas
        print(f"Lote {i}: {len(faltan_lote)} inmuebles faltantes de {len(urls_lote)}")

faltan = urls_totales - urls_procesadas
print(f"Total de inmuebles únicos faltantes: {len(faltan)}")
