import os
import json
from pathlib import Path
from glob import glob

# Rutas de los lotes y backups
base_dir = Path(r"C:/Users/Miguel Martinez SSD/OneDrive - BROWSER TRAVEL SOLUTIONS S.A.S VIAJEMOS/Documentos/PROYECTOS/ARRIENDO DATA SETS/InmueblesFR")
lote_dirs = [base_dir / f"lote_{i:02d}" for i in range(1, 6)]

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

print(f"Total de inmuebles únicos leídos: {len(urls_procesadas)}")
