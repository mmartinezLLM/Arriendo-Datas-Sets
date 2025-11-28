"""
Monitor de progreso en tiempo real para los 15 lotes
"""
import os
import json
from pathlib import Path
from datetime import datetime
import time

LOTES_DIR = "resultados/lotes"

def show_progress():
    """Muestra el progreso actualizado de todos los lotes"""
    print("\n" * 2)
    print("="*100)
    print("MONITOR DE PROGRESO - LOTES 1-15")
    print("="*100)
    print(f"Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    total_exitosas = 0
    total_fallidas = 0
    total_procesadas = 0
    
    for lote_num in range(1, 16):
        lote_dir = os.path.join(LOTES_DIR, f'lote_{lote_num:02d}')
        
        # Buscar JSON más reciente
        json_files = sorted(Path(lote_dir).glob('lote_*.json'))
        
        if not json_files:
            print(f"Lote {lote_num:02d}: Sin datos aún")
            continue
        
        try:
            with open(json_files[-1], 'r', encoding='utf-8') as f:
                props = json.load(f)
            
            total = len(props)
            exitosas = sum(1 for p in props if p.get('COD FR'))
            fallidas = total - exitosas
            
            total_exitosas += exitosas
            total_fallidas += fallidas
            total_procesadas += total
            
            tasa = (exitosas / total * 100) if total > 0 else 0
            
            print(f"Lote {lote_num:02d}: {exitosas:>5,} ✓ | {fallidas:>5,} ✗ | {total:>6,} total | {tasa:>5.1f}%")
            
        except Exception as e:
            print(f"Lote {lote_num:02d}: Error leyendo JSON - {e}")
    
    print("-" * 100)
    if total_procesadas > 0:
        tasa_global = (total_exitosas / total_procesadas * 100)
        print(f"TOTAL: {total_exitosas:>5,} ✓ | {total_fallidas:>5,} ✗ | {total_procesadas:>6,} total | {tasa_global:>5.1f}%")
    else:
        print("TOTAL: Procesando...")
    print("=" * 100 + "\n")

if __name__ == '__main__':
    while True:
        try:
            show_progress()
            time.sleep(5)  # Actualizar cada 5 segundos
        except KeyboardInterrupt:
            print("\nMonitor detenido")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
