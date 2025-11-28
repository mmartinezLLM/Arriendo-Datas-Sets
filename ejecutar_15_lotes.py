"""
Ejecuta todos los 10 lotes en paralelo con manejo robusto de procesos
"""
import subprocess
import time
import os
from datetime import datetime
from pathlib import Path
import sys

LOTES = list(range(1, 11))  # Cambiado de 1 a 15 a 1 a 10

def limpiar_progreso_anterior():
    """Limpia archivos de progreso anterior pero preserva checkpoints"""
    print("Limpiando archivos de progreso anterior...")
    lotes_dir = "resultados/lotes"
    
    for lote_num in LOTES:
        lote_dir = os.path.join(lotes_dir, f'lote_{lote_num:02d}')
        progreso_file = os.path.join(lote_dir, 'progreso.txt')
        
        if os.path.exists(progreso_file):
            try:
                os.remove(progreso_file)
                print(f"  Limpiado: {progreso_file}")
            except:
                pass

def ejecutar_lotes():
    """Ejecuta todos los lotes en paralelo"""
    print("="*80)
    print("EJECUTANDO 10 LOTES EN PARALELO (CON RETRY LOGIC)")  # Actualizado a 10 lotes
    print("="*80)
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    limpiar_progreso_anterior()
    
    procesos = {}
    
    print("\nIniciando procesos...")
    print("-"*80)
    
    for lote_num in LOTES:
        # Crear comando para ejecutar lote
        cmd = [
            sys.executable,
            "procesar_lote.py",
            str(lote_num)
        ]
        
        # Ejecutar en nueva ventana (Windows) o en background
        try:
            # Usar CREATE_NEW_CONSOLE para Windows
            proceso = subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=os.getcwd()
            )
            procesos[lote_num] = proceso
            print(f"✓ Lote {lote_num:02d} iniciado (PID: {proceso.pid})")
            time.sleep(1)  # Pequeña pausa entre inicios
        except Exception as e:
            print(f"✗ ERROR iniciando Lote {lote_num:02d}: {e}")
    
    print("-"*80)
    print(f"Total de lotes iniciados: {len(procesos)}/10\n")  # Actualizado a 10 lotes
    
    if len(procesos) == 0:
        print("ERROR: No se pudieron iniciar los lotes")
        return
    
    # Monitorear progreso
    print("\nMONITOREANDO PROGRESO...")
    print("="*80)
    print("(Verifica las ventanas abiertas para ver detalles de cada lote)")
    print()
    
    inicio_tiempo = time.time()
    
    while procesos:
        # Verificar estado de cada proceso
        lotes_terminados = []
        
        for lote_num, proceso in list(procesos.items()):
            retcode = proceso.poll()
            
            if retcode is not None:
                # Proceso terminó
                if retcode == 0:
                    print(f"✓ Lote {lote_num:02d} completado exitosamente")
                else:
                    print(f"⚠ Lote {lote_num:02d} terminó con código: {retcode}")
                lotes_terminados.append(lote_num)
            else:
                # Mostrar progreso del lote
                progreso_file = os.path.join("resultados/lotes", f'lote_{lote_num:02d}', 'progreso.txt')
                if os.path.exists(progreso_file):
                    try:
                        with open(progreso_file, 'r', encoding='utf-8') as f:
                            contenido = f.read().strip()
                            if contenido:
                                lineas = contenido.split('\n')
                                print(f"  Lote {lote_num:02d}: {lineas[-1]}")  # Última línea
                    except:
                        pass
        
        # Remover lotes terminados
        for lote_num in lotes_terminados:
            del procesos[lote_num]
        
        if procesos:
            print(f"\nProcesos aún activos: {len(procesos)}")
            time.sleep(10)  # Verificar cada 10 segundos
        
        print()
    
    tiempo_total = time.time() - inicio_tiempo
    
    print("\n" + "="*80)
    print("EJECUCIÓN COMPLETADA")
    print("="*80)
    print(f"Tiempo total: {tiempo_total/3600:.2f} horas ({tiempo_total/60:.1f} minutos)")
    print(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Resumen final
    print("RESUMEN DE RESULTADOS:")
    print("-"*80)
    
    total_exitosas = 0
    total_fallidas = 0
    
    for lote_num in LOTES:
        lote_dir = os.path.join("resultados/lotes", f'lote_{lote_num:02d}')
        
        # Buscar JSON más reciente
        json_files = sorted(Path(lote_dir).glob('lote_*.json'))
        
        if json_files:
            import json
            with open(json_files[-1], 'r', encoding='utf-8') as f:
                props = json.load(f)
            
            total = len(props)
            exitosas = sum(1 for p in props if p.get('COD FR'))
            fallidas = total - exitosas
            
            total_exitosas += exitosas
            total_fallidas += fallidas
            
            print(f"Lote {lote_num:02d}: {exitosas:,} exitosas | {fallidas:,} fallidas | Total: {total:,}")
        else:
            print(f"Lote {lote_num:02d}: No se encontraron resultados")
    
    print("-"*80)
    print(f"TOTAL: {total_exitosas:,} exitosas | {total_fallidas:,} fallidas")
    if total_exitosas + total_fallidas > 0:
        tasa = (total_exitosas / (total_exitosas + total_fallidas)) * 100
        print(f"Tasa de éxito: {tasa:.2f}%")
    print()

if __name__ == '__main__':
    ejecutar_lotes()
