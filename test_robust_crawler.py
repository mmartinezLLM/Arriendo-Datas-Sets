"""
test_robust_crawler.py - Script de prueba para el crawler robusto

Ejecuta una prueba con 20 URLs reales para validar:
- Checkpoints funcionan
- Reintentos se activan correctamente
- Paralelización no genera conflictos
- Los datos se guardan correctamente
"""
import sys
from property_crawler_robust import crawl_properties_robust

# URLs de prueba con diferentes tipos de inmuebles
urls_test = [
    # Casas
    "https://www.fincaraiz.com.co/casa-en-venta-en-venecia-bogota/192350837",
    "https://www.fincaraiz.com.co/casa-en-venta-en-la-paz-bogota/192026061",
    "https://www.fincaraiz.com.co/casa-en-venta-en-centro-engativa-bogota/192192693",
    "https://www.fincaraiz.com.co/casa-en-venta-en-valladolid-bogota/192350037",
    
    # Apartamentos
    "https://www.fincaraiz.com.co/apartamento-en-venta-en-centro-fontibon-bogota/192006621",
    "https://www.fincaraiz.com.co/apartamento-en-venta-en-venecia-bogota/192313178",
    "https://www.fincaraiz.com.co/apartamento-en-arriendo-en-madelena-bogota/193078099",
    "https://www.fincaraiz.com.co/apartamento-en-venta-en-venecia-bogota/192039579",
    
    # Locales comerciales
    "https://www.fincaraiz.com.co/local-en-arriendo-en-fatima-bogota/192214671",
    "https://www.fincaraiz.com.co/local-en-arriendo-en-alqueria-bogota/192520810",
    "https://www.fincaraiz.com.co/local-en-venta-en-centro-comercial-santafe-bogota/192377140",
    
    # Bodegas
    "https://www.fincaraiz.com.co/bodega-en-venta-en-venecia-bogota/192473528",
    "https://www.fincaraiz.com.co/bodega-en-arriendo-en-alqueria-bogota/192489109",
    "https://www.fincaraiz.com.co/bodega-en-arriendo-en-venecia-bogota/192307736",
    
    # Oficinas
    "https://www.fincaraiz.com.co/oficina-en-arriendo-en-potosi/192114884",
    
    # Lotes
    "https://www.fincaraiz.com.co/lote-en-venta-en-santa-librada-bogota/192527664",
    "https://www.fincaraiz.com.co/lote-en-venta-en-siberia-cota/192934375",
    
    # Fincas
    "https://www.fincaraiz.com.co/finca-en-venta-en-yumbo/192915489",
    "https://www.fincaraiz.com.co/finca-en-venta-en-popayan/192916767",
    
    # Casa-lote
    "https://www.fincaraiz.com.co/casa-lote-en-venta-en-venecia-bogota/192349416",
]


def main():
    print("="*70)
    print("TEST DEL CRAWLER ROBUSTO")
    print("="*70)
    print(f"\nProbando con {len(urls_test)} URLs de diferentes tipos\n")
    
    # Configuración de prueba (agresiva para detectar problemas)
    test_config = {
        'checkpoint_interval': 3,   # Checkpoint cada 3 URLs
        'max_retries': 2,           # Solo 2 reintentos para prueba rápida
        'batch_size': 5,            # Batches pequeños
        'max_workers': 2,           # 2 threads concurrentes
        'request_delay': 0.3,       # Rápido para testing
        'headless': True,
        'page_timeout': 15,
    }
    
    print("Configuración de prueba:")
    for key, value in test_config.items():
        print(f"  {key}: {value}")
    print()
    
    # Ejecutar crawling
    try:
        stats = crawl_properties_robust(
            urls_test,
            output_dir='resultados',
            config=test_config
        )
        
        print("\n" + "="*70)
        print("RESULTADO DE LA PRUEBA")
        print("="*70)
        print(f"Total URLs: {stats['total']}")
        print(f"Exitosas: {stats['success']}")
        print(f"Fallidas: {stats['failed']}")
        print(f"Saltadas (duplicadas): {stats['skipped']}")
        print(f"Duración: {stats['duration_seconds']:.1f}s")
        print(f"Tasa: {stats['rate_per_second']:.2f} propiedades/seg")
        
        # Validaciones
        print("\nValidaciones:")
        success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"  Tasa de éxito: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("  ✓ Tasa de éxito BUENA (>=80%)")
        elif success_rate >= 60:
            print("  ⚠ Tasa de éxito ACEPTABLE (60-80%)")
        else:
            print("  ✗ Tasa de éxito BAJA (<60%) - Revisar configuración")
        
        if stats['rate_per_second'] >= 0.5:
            print(f"  ✓ Velocidad BUENA (>= 0.5 props/seg)")
        else:
            print(f"  ⚠ Velocidad LENTA - Considerar aumentar workers o reducir delays")
        
        print("\nArchivos generados en resultados/:")
        print("  - properties_*.jsonl (datos en tiempo real)")
        print("  - properties_*_consolidated.json (JSON final)")
        print("  - checkpoint_*.json (estado de sesión)")
        print("  - errors_*.jsonl (errores)")
        print("  - crawler_*.log (log completo)")
        
        print("\nPara generar Excel:")
        print("  python json_to_excel_properties.py resultados/properties_*_consolidated.json")
        
        return 0 if success_rate >= 60 else 1
        
    except KeyboardInterrupt:
        print("\n\nPrueba interrumpida por usuario")
        print("Puedes reanudarla ejecutando este script nuevamente")
        return 130
    except Exception as e:
        print(f"\n\nERROR durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
