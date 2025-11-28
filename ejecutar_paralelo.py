"""
Script para ejecutar los 10 lotes en paralelo
Cada lote se ejecuta en su propio proceso de Python
"""
import subprocess
import os
import time
from datetime import datetime

def ejecutar_paralelo():
    print("="*80)
    print("EJECUCIÓN PARALELA DE 10 LOTES")
    print("="*80)
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("Iniciando 10 procesos en paralelo...")
    print("Cada lote procesará una parte de las URLs")
    print()
    
    # Lista para almacenar los procesos
    procesos = []
    
    # Iniciar los 10 lotes en paralelo
    for i in range(1, 11):
        print(f"Iniciando Lote {i:2d}...", end=" ")
        
        # Crear proceso en segundo plano
        proceso = subprocess.Popen(
            ['python', 'procesar_lote.py', str(i)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        procesos.append({
            'numero': i,
            'proceso': proceso,
            'pid': proceso.pid
        })
        
        print(f"✓ PID: {proceso.pid}")
        
        # Pequeña pausa entre inicios para evitar sobrecarga
        time.sleep(1)
    
    print()
    print("="*80)
    print(f"TODOS LOS {len(procesos)} LOTES INICIADOS")
    print("="*80)
    print()
    print("INFORMACIÓN DE PROCESOS:")
    for p in procesos:
        print(f"  Lote {p['numero']:2d}: PID {p['pid']}")
    
    print()
    print("IMPORTANTE:")
    print("  - Cada lote corre en su propia ventana de consola")
    print("  - Puedes cerrar esta ventana, los procesos continuarán")
    print("  - Monitorea el progreso en: resultados/lotes/lote_XX/progreso.txt")
    print("  - Para detener un lote específico, cierra su ventana de consola")
    print()
    print("Para ver el estado de todos los procesos:")
    print("  python estado_lotes.py")
    print()
    print("Presiona Ctrl+C para salir de este monitor (no detiene los lotes)")
    
    try:
        # Monitoreo simple
        while True:
            time.sleep(60)  # Revisar cada minuto
            activos = sum(1 for p in procesos if p['proceso'].poll() is None)
            completados = len(procesos) - activos
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Estado: {activos} activos, {completados} completados")
            
            if activos == 0:
                print("\n¡Todos los lotes completados!")
                break
                
    except KeyboardInterrupt:
        print("\n\nMonitor detenido. Los procesos continúan ejecutándose.")
        print("Para ver el estado usa: python estado_lotes.py")

if __name__ == '__main__':
    ejecutar_paralelo()
