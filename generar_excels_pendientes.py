import os
import json
import pandas as pd
from pathlib import Path
from glob import glob

# Rutas de los lotes y backups
base_dir = Path(r"C:/Users/Miguel Martinez SSD/OneDrive - BROWSER TRAVEL SOLUTIONS S.A.S VIAJEMOS/Documentos/PROYECTOS/ARRIENDO DATA SETS/InmueblesFR")
lote_dirs = [base_dir / f"lote_{i:02d}" for i in range(1, 6)]

# 1. Recolectar todas las URLs ya procesadas en todos los backups
urls_procesadas = set()
for lote_dir in lote_dirs:
    backups = sorted(glob(str(lote_dir / f"lote_*_backup_*.json")))
    if not backups:
        continue
    # Tomar el backup más grande (último por cantidad de registros)
    backups.sort(key=lambda x: int(x.split('_backup_')[1].split('_')[0]), reverse=True)
    latest_backup = backups[0]
    with open(latest_backup, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            for d in data:
                url = d.get('url_inmueble')
                if url:
                    urls_procesadas.add(url)
        except Exception as e:
            print(f"Error leyendo {latest_backup}: {e}")

# 2. Leer los excels originales de cada lote y filtrar URLs pendientes
for i, lote_dir in enumerate(lote_dirs, 1):
    excel_path = lote_dir / f"inmuebles_lote_{i:02d}.xlsx"
    if not excel_path.exists():
        print(f"No existe: {excel_path}")
        continue
    df = pd.read_excel(excel_path)
    if 'URL' not in df.columns:
        print(f"No hay columna 'URL' en {excel_path}")
        continue
    urls = df['URL'].dropna().tolist()
    urls_pendientes = [u for u in urls if u not in urls_procesadas]
    print(f"Lote {i}: {len(urls_pendientes)} URLs pendientes de {len(urls)}")
    # Guardar nuevo Excel solo con pendientes
    df_pend = df[df['URL'].isin(urls_pendientes)]
    out_path = lote_dir / f"inmuebles_lote_{i:02d}_pendientes.xlsx"
    df_pend.to_excel(out_path, index=False)
    print(f"Guardado: {out_path}")
