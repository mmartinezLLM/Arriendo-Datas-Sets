"""
Script para procesar URLs fallidas desde archivos JSON existentes
Extrae las URLs fallidas y las reintenta
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from property_crawler_selenium import PropertyCrawlerSelenium, _formatear_salida_final
import time

LOTES_DIR = "resultados/lotes"

def procesar_fallidas(numero_lote: int):
    """
    Procesa solo las URLs que fallaron en un lote anterior
    """
    print("="*80)
    print(f"REPROCESANDO FALLIDAS - LOTE {numero_lote}/15")
    print("="*80)
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Buscar archivos JSON del lote
    lote_dir = os.path.join(LOTES_DIR, f'lote_{numero_lote:02d}')
    
    if not os.path.exists(lote_dir):
        print(f"ERROR: No se encontró el directorio {lote_dir}")
        return
    
    # Buscar todos los JSON del lote
    json_files = sorted(Path(lote_dir).glob('lote_*.json'))
    
    if not json_files:
        print(f"No se encontraron archivos JSON en {lote_dir}")
        return
    
    latest_json = json_files[-1]
    print(f"Leyendo: {latest_json}")
    
    with open(latest_json, 'r', encoding='utf-8') as f:
        propiedades = json.load(f)
    
    print(f"Total de propiedades en JSON: {len(propiedades):,}")
    
    # Identificar fallidas (sin código FR o sin datos esenciales)
    fallidas = []
    para_reintentar = []
    
    for prop in propiedades:
        if not prop.get('COD FR'):
            # Fallida - sin datos
            url = prop.get('URL INMUEBLE')
            if url:
                para_reintentar.append(url)
                fallidas.append(prop)
    
    print(f"URLs para reintentar: {len(para_reintentar):,}")
    
    if not para_reintentar:
        print("\n✓ No hay URLs fallidas para reintentar")
        return
    
    # Procesar URLs fallidas
    print(f"\nIniciando reintento de URLs fallidas...")
    
    crawler = PropertyCrawlerSelenium()
    resultados_exitosos = []
    resultados_fallidos = []
    
    inicio_tiempo = time.time()
    
    try:
        for i, url in enumerate(para_reintentar, 1):
            if i % 50 == 0 or i == 1:
                transcurrido = time.time() - inicio_tiempo
                velocidad = i / transcurrido if transcurrido > 0 else 0
                restantes = len(para_reintentar) - i
                tiempo_estimado = restantes / velocidad if velocidad > 0 else 0
                
                print(f"\n[{i}/{len(para_reintentar)}] Progreso: {i/len(para_reintentar)*100:.1f}%")
                print(f"  Exitosas: {len(resultados_exitosos)} | Fallidas: {len(resultados_fallidos)}")
                print(f"  Velocidad: {velocidad:.2f} URLs/seg")
                print(f"  Tiempo estimado: {tiempo_estimado/60:.1f} minutos")
            
            try:
                datos_raw = crawler.extraer_propiedad(url)
                
                if datos_raw and datos_raw.get('codigo_fr'):
                    datos_final = _formatear_salida_final(datos_raw)
                    resultados_exitosos.append(datos_final)
                    print(f"  ✓ URL exitosa")
                else:
                    resultados_fallidos.append(url)
                    print(f"  ✗ URL sin datos")
                    
            except Exception as e:
                resultados_fallidos.append(url)
                print(f"  ✗ Error: {type(e).__name__}")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n⚠ Proceso interrumpido")
    
    finally:
        crawler.close()
        
        # Guardar resultados
        print(f"\n{'='*80}")
        print("GUARDANDO RESULTADOS")
        print("="*80)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Guardar exitosas
        if resultados_exitosos:
            exitosas_json = os.path.join(lote_dir, f'fallidas_reprocessadas_{timestamp}.json')
            with open(exitosas_json, 'w', encoding='utf-8') as f:
                json.dump(resultados_exitosos, f, ensure_ascii=False, indent=2)
            print(f"✓ Exitosas guardadas: {exitosas_json}")
            print(f"  Total: {len(resultados_exitosos):,}")
        
        # Guardar fallidas para siguiente intento
        if resultados_fallidos:
            fallidas_txt = os.path.join(lote_dir, f'fallidas_{timestamp}.txt')
            with open(fallidas_txt, 'w', encoding='utf-8') as f:
                for url in resultados_fallidos:
                    f.write(f"{url}\n")
            print(f"✓ Fallidas guardadas para reintentar: {fallidas_txt}")
            print(f"  Total: {len(resultados_fallidos):,}")
        
        # Resumen
        print(f"\n{'='*80}")
        print("RESUMEN")
        print("="*80)
        print(f"URLs procesadas: {len(resultados_exitosos) + len(resultados_fallidos):,}")
        print(f"Exitosas: {len(resultados_exitosos):,}")
        print(f"Fallidas: {len(resultados_fallidos):,}")
        if len(resultados_exitosos) + len(resultados_fallidos) > 0:
            tasa = (len(resultados_exitosos) / (len(resultados_exitosos) + len(resultados_fallidos))) * 100
            print(f"Tasa de éxito: {tasa:.2f}%")
        print()

def main():
    if len(sys.argv) < 2:
        print("Uso: python procesar_fallidas.py <numero_lote>")
        print("Ejemplo: python procesar_fallidas.py 1")
        print("\nReprocesa solo las URLs que fallaron en un lote anterior")
        sys.exit(1)
    
    try:
        numero_lote = int(sys.argv[1])
        if numero_lote < 1 or numero_lote > 15:
            print("ERROR: El número de lote debe estar entre 1 y 15")
            sys.exit(1)
        
        procesar_fallidas(numero_lote)
        
    except ValueError:
        print("ERROR: El número de lote debe ser un entero")
        sys.exit(1)

if __name__ == '__main__':
    main()
