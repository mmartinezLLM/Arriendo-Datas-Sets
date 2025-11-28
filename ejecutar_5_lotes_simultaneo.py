import subprocess
from pathlib import Path
import os

# Carpeta donde están los archivos de lotes
lotes_dir = Path(r"C:/Users/Miguel Martinez SSD/OneDrive - BROWSER TRAVEL SOLUTIONS S.A.S VIAJEMOS/Documentos/PROYECTOS/ARRIENDO DATA SETS/InmueblesFR")


# Nombres de los archivos de los 5 lotes (ahora en su carpeta de lote)
lote_files = [
    lotes_dir / f"lote_{i:02d}" / f"inmuebles_lote_{i:02d}.xlsx" for i in range(1, 6)
]

# Script de procesamiento
procesar_script = Path("scraper_inmobiliarias/procesar_lote_limpio.py").absolute()

# Lanzar un proceso por cada lote
processes = []
for idx, lote_file in enumerate(lote_files, 1):
    cmd = [
        "python",
        str(procesar_script),
        str(idx),
        str(lote_file)  # Pasar la ruta del Excel como argumento
    ]
    print(f"Lanzando proceso para lote {idx}: {lote_file}")
    p = subprocess.Popen(cmd)
    processes.append(p)

# Esperar a que todos terminen
for p in processes:
    p.wait()
print("Todos los lotes han terminado.")
