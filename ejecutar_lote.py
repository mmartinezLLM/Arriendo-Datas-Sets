import sys
from pathlib import Path
import subprocess

if len(sys.argv) < 2:
    print("Uso: python ejecutar_lote.py <numero_lote>")
    sys.exit(1)

lote_num = int(sys.argv[1])
lote_str = f"{lote_num:02d}"

# Ruta al archivo Excel del lote
lote_file = Path(r"C:/Users/Miguel Martinez SSD/OneDrive - BROWSER TRAVEL SOLUTIONS S.A.S VIAJEMOS/Documentos/PROYECTOS/ARRIENDO DATA SETS/InmueblesFR") / f"inmuebles_lote_{lote_str}.xlsx"

if not lote_file.exists():
    print(f"No existe el archivo: {lote_file}")
    sys.exit(1)

# Ejecutar el procesamiento del lote pasando la ruta del Excel
subprocess.run([
    sys.executable,
    "scraper_inmobiliarias/procesar_lote_limpio.py",
    lote_str,
    str(lote_file)
])
