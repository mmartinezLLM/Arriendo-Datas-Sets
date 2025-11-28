"""
Script para procesar un lote específico de URLs usando el crawler robusto
Uso: python procesar_lote.py <numero_lote>
Ejemplo: python procesar_lote.py 1
"""
import sys
import os
from datetime import datetime
from pathlib import Path
from property_crawler_selenium import PropertyCrawlerSelenium, _formatear_salida_final
import json
import time

LOTES_DIR = "resultados/lotes"

def procesar_lote(numero_lote: int):
    """
    Procesa un lote específico con checkpoint automático cada 100 URLs
    """
    print("="*80)
    print(f"PROCESANDO LOTE {numero_lote}/10")  # Cambiado de 15 a 10
    print("="*80)
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Cargar URLs del lote desde archivo JSON
    urls_file = os.path.join(LOTES_DIR, f'lote_{numero_lote:02d}.json')  # Cambiado a .json
    if not os.path.exists(urls_file):
        print(f"ERROR: No se encontró el archivo {urls_file}")
        print("Ejecuta primero: python dividir_urls_en_lotes.py")
        return
    
    with open(urls_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        urls = data.get("urls", [])
    
    print(f"URLs a procesar: {len(urls):,}")
    
    # Archivos de salida
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = os.path.join(LOTES_DIR, f'lote_{numero_lote:02d}')
    os.makedirs(output_dir, exist_ok=True)
    
    checkpoint_file = os.path.join(output_dir, f'checkpoint_lote_{numero_lote:02d}.jsonl')
    final_json = os.path.join(output_dir, f'lote_{numero_lote:02d}_{timestamp}.json')
    final_excel = os.path.join(output_dir, f'lote_{numero_lote:02d}_{timestamp}.xlsx')
    progress_file = os.path.join(output_dir, 'progreso.txt')
    
    # Verificar si existe checkpoint previo
    procesadas = set()
    resultados = []
    
    if os.path.exists(checkpoint_file):
        print(f"\n¡Checkpoint encontrado! Cargando progreso previo...")
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    item = json.loads(line.strip())
                    resultados.append(item)
                    procesadas.add(item.get('URL INMUEBLE'))
                except:
                    pass
        print(f"URLs ya procesadas: {len(procesadas):,}")
        urls = [url for url in urls if url not in procesadas]
        print(f"URLs pendientes: {len(urls):,}")
    
    if not urls:
        print("\n¡Lote ya completado!")
        return
    
    # Inicializar crawler
    print(f"\nIniciando crawler...")
    crawler = PropertyCrawlerSelenium()
    
    # Contadores
    exitosas = len(procesadas)
    fallidas = 0
    inicio_tiempo = time.time()
    
    try:
        for i, url in enumerate(urls, 1):
            idx_total = exitosas + fallidas + i
            
            # Mostrar progreso cada 10 URLs
            if i % 10 == 0 or i == 1:
                transcurrido = time.time() - inicio_tiempo
                velocidad = idx_total / transcurrido if transcurrido > 0 else 0
                restantes = len(urls) - i
                tiempo_estimado = restantes / velocidad if velocidad > 0 else 0
                
                print(f"\n[{idx_total}/{len(urls)+len(procesadas)}] Progreso: {idx_total/(len(urls)+len(procesadas))*100:.1f}%")
                print(f"  Exitosas: {exitosas} | Fallidas: {fallidas}")
                print(f"  Velocidad: {velocidad:.2f} URLs/seg")
                print(f"  Tiempo estimado restante: {tiempo_estimado/60:.1f} minutos")
            
            try:
                # Extraer datos raw
                datos_raw = crawler.extraer_propiedad(url)
                
                if datos_raw and datos_raw.get('codigo_fr'):
                    # Convertir a formato final
                    datos_final = _formatear_salida_final(datos_raw)
                    resultados.append(datos_final)
                    exitosas += 1
                    
                    # Guardar checkpoint cada 100 URLs
                    if exitosas % 100 == 0:
                        with open(checkpoint_file, 'a', encoding='utf-8') as f:
                            f.write(json.dumps(datos_final, ensure_ascii=False) + '\n')
                        
                        # Actualizar archivo de progreso
                        with open(progress_file, 'w', encoding='utf-8') as f:
                            f.write(f"Lote: {numero_lote}\n")
                            f.write(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write(f"Procesadas: {exitosas}\n")
                            f.write(f"Fallidas: {fallidas}\n")
                            f.write(f"Total: {len(urls)+len(procesadas)}\n")
                            f.write(f"Progreso: {exitosas/(len(urls)+len(procesadas))*100:.1f}%\n")
                        
                        print(f"  ✓ Checkpoint guardado ({exitosas} propiedades)")
                else:
                    fallidas += 1
                    
            except Exception as e:
                fallidas += 1
                print(f"  ✗ Error en {url}: {str(e)[:100]}")
            
            # Pausa entre requests (2 segundos)
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n⚠ Proceso interrumpido por el usuario")
        print("El progreso ha sido guardado en el checkpoint")
    
    finally:
        # Cerrar crawler
        crawler.close()
        
        # Guardar resultados finales
        print(f"\n{'='*80}")
        print("GUARDANDO RESULTADOS FINALES")
        print("="*80)
        
        # Guardar JSON
        with open(final_json, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        print(f"✓ JSON guardado: {final_json}")
        print(f"  Propiedades: {len(resultados):,}")
        
        # Generar Excel
        try:
            from json_to_excel_properties import json_to_excel
            json_to_excel(final_json, final_excel)
            print(f"✓ Excel guardado: {final_excel}")
        except Exception as e:
            print(f"✗ Error al generar Excel: {e}")
        
        # Resumen final
        tiempo_total = time.time() - inicio_tiempo
        print(f"\n{'='*80}")
        print(f"LOTE {numero_lote} COMPLETADO")
        print("="*80)
        print(f"Tiempo total: {tiempo_total/60:.1f} minutos")
        print(f"URLs procesadas: {exitosas + fallidas:,}")
        print(f"Exitosas: {exitosas:,} ({exitosas/(exitosas+fallidas)*100:.1f}%)")
        print(f"Fallidas: {fallidas:,} ({fallidas/(exitosas+fallidas)*100:.1f}%)")
        print(f"Velocidad promedio: {(exitosas+fallidas)/tiempo_total:.2f} URLs/seg")
        print(f"\nArchivos generados:")
        print(f"  - JSON: {final_json}")
        print(f"  - Excel: {final_excel}")
        print(f"  - Checkpoint: {checkpoint_file}")
        print()

def main():
    if len(sys.argv) < 2:
        print("Uso: python procesar_lote.py <numero_lote>")
        print("Ejemplo: python procesar_lote.py 1")
        print("\nLotes disponibles: 1-10")
        return 1
    
    try:
        numero_lote = int(sys.argv[1])
        if numero_lote < 1 or numero_lote > 10:
            print("ERROR: El número de lote debe estar entre 1 y 10")
            return 1
        
        procesar_lote(numero_lote)
        return 0
        
    except ValueError as e:
        print(f"ERROR: El número de lote debe ser un entero (recibido: {sys.argv[1]})")
        return 1
    except Exception as e:
        print(f"ERROR inesperado: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
