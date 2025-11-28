# Procesar lotes

import sys
import json
from pathlib import Path
from datetime import datetime
from property_crawler_selenium import PropertyCrawlerSelenium
import pandas as pd  

def procesar_lote(numero_lote):
    """Procesa todas las URLs de un lote"""
    
    lote_str = f"{numero_lote:02d}"
    # Nueva ruta para backups y resultados 
    output_base_dir = Path(r"C:/Users/Miguel Martinez SSD/OneDrive - BROWSER TRAVEL SOLUTIONS S.A.S VIAJEMOS/Documentos/PROYECTOS/ARRIENDO DATA SETS/InmueblesFR")
    output_base_dir.mkdir(parents=True, exist_ok=True)
    lote_dir = output_base_dir / f"lote_{lote_str}"
    lote_dir.mkdir(parents=True, exist_ok=True)

    # Permitir pasar la ruta del Excel como argumento de base
    if len(sys.argv) > 2:
        excel_file = Path(sys.argv[2])
    else:
        excel_file = Path("inmuebles.xlsx")

    if not excel_file.exists():
        print(f"❌ Archivo Excel no encontrado: {excel_file}")
        return

    # Excel
    try:
        import pandas as pd 
        df = pd.read_excel(excel_file)
        if 'URL' not in df.columns:
            print("❌ La columna 'URL' no se encuentra en el archivo Excel.")
            return
        urls = df['URL'].dropna().tolist()
    except Exception as e:
        print(f"❌ Error al leer el archivo Excel: {str(e)}")
        return

    # Reanudación automática desde backup 
    import re
    backup_files = list(lote_dir.glob(f"lote_{lote_str}_backup_*.json"))
    latest_backup = None
    latest_index = 0
    if backup_files:
        # Buscar el backup
        def extract_index(f):
            m = re.search(r"backup_(\d+)_", f.name)
            return int(m.group(1)) if m else 0
        backup_files.sort(key=extract_index, reverse=True)
        latest_backup = backup_files[0]
        latest_index = extract_index(latest_backup)
    resultados = []
    exitosas = 0
    fallidas = 0
    if latest_backup:
        print(f"🔄 Reanudando desde backup: {latest_backup}")
        with open(latest_backup, 'r', encoding='utf-8') as f:
            resultados = json.load(f)
        exitosas = len(resultados)
        # Solo procesar las URLs que faltan
        urls = urls[latest_index:]
    else:
        print("▶️ Procesando desde el inicio (sin backup previo)")

    print(f"\n{'='*70}")
    print(f"LOTE {lote_str} - Total de URLs: {len(urls) + exitosas} (pendientes: {len(urls)})")
    print(f"{'='*70}\n")

    # Crawler
    crawler = PropertyCrawlerSelenium(headless=True)

    log_file = lote_dir / f"lote_{lote_str}_errores.log"

    try:
        for i, url in enumerate(urls, 1):
            global_index = exitosas + i  # Ya procesados en LOG
            if global_index % 200 == 0:
                print(f"[{global_index:5d}/{len(urls) + exitosas}] ✓{exitosas:5d} | ✗{fallidas:5d}")

            try:
                # Extraer propiedad con reintentos (3 reintentos)
                datos_raw = crawler.extraer_propiedad(url)

                if datos_raw and datos_raw.get('cod_fr'):
                    resultados.append(datos_raw)
                    exitosas += 1
                else:
                    fallidas += 1
                    with open(log_file, 'a', encoding='utf-8') as log:
                        log.write(f"URL sin datos válidos: {url}\n")

            except Exception as e:
                fallidas += 1
                with open(log_file, 'a', encoding='utf-8') as log:
                    log.write(f"Error en URL {url}: {str(e)}\n")

            # Guardar backup cada 200 inmuebles
            if global_index % 200 == 0 or i == len(urls):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = lote_dir / f"lote_{lote_str}_backup_{global_index}_{timestamp}.json"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(resultados, f, ensure_ascii=False, indent=2)
                print(f"Backup guardado: {backup_file}")

        # Guardar resultados finales
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_json = lote_dir / f"lote_{lote_str}_{timestamp}.json"
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)

        # Guardar JSON, CSV y el Eczel
        df_result = pd.DataFrame(resultados)
        output_csv = lote_dir / f"lote_{lote_str}_{timestamp}.csv"
        output_xlsx = lote_dir / f"lote_{lote_str}_{timestamp}.xlsx"
        df_result.to_csv(output_csv, index=False, encoding='utf-8-sig')
        df_result.to_excel(output_xlsx, index=False)

        print(f"\n{'='*70}")
        print(f"LOTE {lote_str} - COMPLETADO")
        print(f"{'='*70}")
        print(f"✓ Exitosas: {exitosas}")
        print(f"✗ Fallidas: {fallidas}")
        print(f"📁 JSON: {output_json}")
        print(f"📁 CSV: {output_csv}")
        print(f"📁 XLSX: {output_xlsx}")
        print(f"📄 Log de errores: {log_file}")
        print(f"{'='*70}\n")

    finally:
        try:
            crawler.close()
        except:
            pass
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python procesar_lote_limpio.py <numero_lote> [ruta_excel]")
        sys.exit(1)

    try:
        numero_lote = int(sys.argv[1])
        procesar_lote(numero_lote)
    except ValueError:
        print(f"Error: {sys.argv[1]} no es un número válido")
        sys.exit(1)
# Auf Die Knie Blue Lock (inserte rosa azul)