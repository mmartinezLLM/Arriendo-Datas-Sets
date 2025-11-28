"""
Script para procesar 277,953 URLs en 10 lotes usando el crawler robusto
Cada lote se procesará de forma independiente con checkpoints
"""
import pandas as pd
import os
import sys
from datetime import datetime
from pathlib import Path

# Archivo de entrada
INPUT_FILE = r"C:\Users\Miguel Martinez SSD\OneDrive - BROWSER TRAVEL SOLUTIONS S.A.S VIAJEMOS\Documentos\PROYECTOS\ARRIENDO DATA SETS\Inmuebles.xlsx"
OUTPUT_DIR = "resultados/lotes"

def main():
    print("="*80)
    print("DIVISIÓN DE URLS EN 10 LOTES")
    print("="*80)
    
    # Leer archivo de inmuebles
    print(f"\nLeyendo archivo: {INPUT_FILE}")
    df = pd.read_excel(INPUT_FILE)
    
    total_urls = len(df)
    print(f"Total URLs encontradas: {total_urls:,}")
    
    # Calcular tamaño de cada lote
    num_lotes = 15
    urls_por_lote = total_urls // num_lotes
    print(f"\nDividiendo en {num_lotes} lotes de ~{urls_por_lote:,} URLs cada uno")
    
    # Crear directorio de salida
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Dividir y guardar lotes
    urls = df['Inmuebles'].tolist()
    
    for i in range(num_lotes):
        inicio = i * urls_por_lote
        # Último lote toma todas las URLs restantes
        fin = (i + 1) * urls_por_lote if i < num_lotes - 1 else total_urls
        
        lote_urls = urls[inicio:fin]
        
        # Guardar archivo de lote
        lote_file = os.path.join(OUTPUT_DIR, f'lote_{i+1:02d}_urls.txt')
        with open(lote_file, 'w', encoding='utf-8') as f:
            for url in lote_urls:
                f.write(f"{url}\n")
        
        print(f"  Lote {i+1:2d}: {len(lote_urls):6,} URLs -> {lote_file}")
    
    # Crear script de ejecución para cada lote
    print(f"\n{'='*80}")
    print("CREANDO SCRIPTS DE EJECUCIÓN")
    print("="*80)
    
    for i in range(1, num_lotes + 1):
        script_content = f"""@echo off
REM Script para ejecutar Lote {i} de 10
echo ================================================================================
echo PROCESANDO LOTE {i}/10
echo ================================================================================
echo.

cd /d "%~dp0.."
python procesar_lote.py {i}

echo.
echo ================================================================================
echo LOTE {i} COMPLETADO
echo ================================================================================
pause
"""
        script_file = os.path.join(OUTPUT_DIR, f'ejecutar_lote_{i:02d}.bat')
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print(f"  Script creado: {script_file}")
    
    print(f"\n{'='*80}")
    print("RESUMEN")
    print("="*80)
    print(f"\nTotal URLs: {total_urls:,}")
    print(f"Lotes creados: {num_lotes}")
    print(f"Archivos de URLs: {OUTPUT_DIR}/lote_XX_urls.txt")
    print(f"Scripts de ejecución: {OUTPUT_DIR}/ejecutar_lote_XX.bat")
    print(f"\nPara procesar cada lote, ejecuta:")
    print(f"  python procesar_lote.py <numero_lote>")
    print(f"\nO ejecuta todos en paralelo con:")
    print(f"  python ejecutar_paralelo.py")
    print()

if __name__ == '__main__':
    main()
