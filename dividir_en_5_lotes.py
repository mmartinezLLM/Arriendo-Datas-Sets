import pandas as pd
from pathlib import Path
import math


# Ruta del archivo Excel original (el más grande y actualizado)
excel_file = Path(r"C:/Users/Miguel Martinez SSD/OneDrive - BROWSER TRAVEL SOLUTIONS S.A.S VIAJEMOS/Documentos/PROYECTOS/ARRIENDO DATA SETS/InmueblesFR/inmuebles.xlsx")

# Nueva carpeta de salida para los lotes
output_base_dir = Path(r"C:/Users/Miguel Martinez SSD/OneDrive - BROWSER TRAVEL SOLUTIONS S.A.S VIAJEMOS/Documentos/PROYECTOS/ARRIENDO DATA SETS/InmueblesFR")
output_base_dir.mkdir(parents=True, exist_ok=True)

# Leer el archivo Excel
df = pd.read_excel(excel_file)
if 'URL' not in df.columns:
    raise Exception("La columna 'URL' no se encuentra en el archivo Excel.")

urls = df['URL'].dropna().tolist()
total = len(urls)
lotes = 5
urls_por_lote = math.ceil(total / lotes)

for i in range(lotes):
    inicio = i * urls_por_lote
    fin = min((i + 1) * urls_por_lote, total)
    df_lote = df.iloc[inicio:fin]
    # Crear carpeta del lote si no existe
    lote_dir = output_base_dir / f"lote_{i+1:02d}"
    lote_dir.mkdir(parents=True, exist_ok=True)
    lote_path = lote_dir / f"inmuebles_lote_{i+1:02d}.xlsx"
    df_lote.to_excel(lote_path, index=False)
    print(f"Lote {i+1}: {lote_path} ({len(df_lote)} URLs)")
