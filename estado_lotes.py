"""
Script para verificar el estado de todos los lotes en ejecución
"""
import os
import glob
from datetime import datetime

def leer_progreso(numero_lote):
    """Lee el archivo de progreso de un lote"""
    progreso_file = f'resultados/lotes/lote_{numero_lote:02d}/progreso.txt'
    
    if not os.path.exists(progreso_file):
        return None
    
    info = {}
    try:
        with open(progreso_file, 'r', encoding='utf-8') as f:
            for line in f:
                if ':' in line:
                    key, value = line.strip().split(':', 1)
                    info[key.strip()] = value.strip()
        return info
    except:
        return None

def contar_checkpoint(numero_lote):
    """Cuenta las URLs en el checkpoint"""
    checkpoint_file = f'resultados/lotes/lote_{numero_lote:02d}/checkpoint_lote_{numero_lote:02d}.jsonl'
    
    if not os.path.exists(checkpoint_file):
        return 0
    
    try:
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except:
        return 0

def main():
    print("="*100)
    print("ESTADO DE TODOS LOS LOTES")
    print("="*100)
    print(f"Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print(f"{'Lote':<6} {'URLs':<10} {'Procesadas':<12} {'Fallidas':<10} {'Progreso':<12} {'Última Actualización':<20}")
    print("-"*100)
    
    total_procesadas = 0
    total_fallidas = 0
    lotes_activos = 0
    lotes_completados = 0
    lotes_no_iniciados = 0
    
    for i in range(1, 21):
        progreso = leer_progreso(i)
        checkpoint_count = contar_checkpoint(i)
        
        if progreso:
            procesadas = int(progreso.get('Procesadas', '0'))
            fallidas = int(progreso.get('Fallidas', '0'))
            total = int(progreso.get('Total', '0'))
            porcentaje = progreso.get('Progreso', '0%')
            ultima = progreso.get('Última actualización', 'N/A')
            
            total_procesadas += procesadas
            total_fallidas += fallidas
            
            if porcentaje == '100.0%':
                lotes_completados += 1
                status = "✓"
            else:
                lotes_activos += 1
                status = "→"
            
            print(f"{status} {i:2d}   {total:<10,} {procesadas:<12,} {fallidas:<10,} {porcentaje:<12} {ultima:<20}")
        elif checkpoint_count > 0:
            # Hay checkpoint pero no progreso actual
            print(f"⚠ {i:2d}   {'~13,897':<10} {checkpoint_count:<12,} {'?':<10} {'?':<12} {'Checkpoint encontrado':<20}")
            lotes_activos += 1
        else:
            # No iniciado
            print(f"○ {i:2d}   {'~13,897':<10} {0:<12} {0:<10} {'0%':<12} {'No iniciado':<20}")
            lotes_no_iniciados += 1
    
    print("-"*100)
    print(f"\nRESUMEN:")
    print(f"  Lotes completados: {lotes_completados}")
    print(f"  Lotes activos: {lotes_activos}")
    print(f"  Lotes no iniciados: {lotes_no_iniciados}")
    print(f"\n  Total URLs procesadas: {total_procesadas:,}")
    print(f"  Total URLs fallidas: {total_fallidas:,}")
    print(f"  Total extraídas exitosamente: {total_procesadas - total_fallidas:,}")
    
    if total_procesadas > 0:
        tasa_exito = ((total_procesadas - total_fallidas) / total_procesadas) * 100
        print(f"  Tasa de éxito: {tasa_exito:.2f}%")
    
    print()
    print("LEYENDA:")
    print("  ✓ = Completado")
    print("  → = En progreso")
    print("  ⚠ = Con checkpoint (posible pausa)")
    print("  ○ = No iniciado")
    print()

if __name__ == '__main__':
    main()
