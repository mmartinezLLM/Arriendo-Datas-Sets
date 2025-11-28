"""
Script de prueba para verificar el nuevo esquema de 50 columnas
Con 10 URLs de muestra proporcionadas por el usuario
"""
import sys
import time
from datetime import datetime
from property_crawler_selenium import PropertyCrawlerSelenium, _formatear_salida_final
from json_to_excel_properties import json_to_excel
import json

# URLs de prueba
TEST_URLS = [
    "https://www.fincaraiz.com.co/local-en-arriendo-en-belen-rosales-medellin/192805253",
    "https://www.fincaraiz.com.co/casa-en-venta-en-guarne/192383406",
    "https://www.fincaraiz.com.co/apartaestudio-en-venta-en-bello/11019344",
    "https://www.fincaraiz.com.co/casa-campestre-en-venta-en-marinilla/191908150",
    "https://www.fincaraiz.com.co/apartaestudio-en-arriendo-en-estadio-medellin/191997487",
    "https://www.fincaraiz.com.co/lote-en-venta-en-barbosa/191711457",
    "https://www.fincaraiz.com.co/apartamento-en-venta-en-prado-medellin/10992749",
    "https://www.fincaraiz.com.co/apartaestudio-en-arriendo-en-estadio-medellin/192966101",
    "https://www.fincaraiz.com.co/apartamento-en-arriendo-en-urbanizacion-amazonia-bello/193086801",
    "https://www.fincaraiz.com.co/apartamento-en-venta-en-simon-bolivar-medellin/10903156",
]

def main():
    print("="*80)
    print("PRUEBA DEL NUEVO ESQUEMA DE 50 COLUMNAS")
    print("="*80)
    print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URLs a procesar: {len(TEST_URLS)}")
    print()
    
    # Inicializar crawler
    print("Inicializando crawler...")
    crawler = PropertyCrawlerSelenium()
    
    # Procesar URLs
    resultados = []
    exitosos = 0
    fallidos = 0
    
    for i, url in enumerate(TEST_URLS, 1):
        print(f"\n[{i}/{len(TEST_URLS)}] Procesando: {url}")
        try:
            # Extraer datos raw
            datos_raw = crawler.extraer_propiedad(url)
            if datos_raw and datos_raw.get('codigo_fr'):
                # Convertir al formato final
                prop = _formatear_salida_final(datos_raw)
                resultados.append(prop)
                exitosos += 1
                # Mostrar info básica
                print(f"  ✓ Título: {prop.get('TITULO', 'N/A')[:60]}...")
                print(f"  ✓ Tipo: {prop.get('Tipo de inmueble')} - {prop.get('Tipo de oferta')}")
                print(f"  ✓ Precio: {prop.get('PRECIO')}")
                # Contar imágenes
                imgs = sum(1 for j in range(1, 16) if prop.get(f'Imagen {j}'))
                print(f"  ✓ Imágenes: {imgs}")
            else:
                fallidos += 1
                print(f"  ✗ Error: No se pudo extraer la propiedad")
        except Exception as e:
            fallidos += 1
            print(f"  ✗ Error: {str(e)}")
        
        # Pequeña pausa entre requests
        if i < len(TEST_URLS):
            time.sleep(2)
    
    # Cerrar crawler
    crawler.close()
    
    # Guardar resultados
    print("\n" + "="*80)
    print("GUARDANDO RESULTADOS")
    print("="*80)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_file = f'resultados/test_esquema_{timestamp}.json'
    excel_file = f'resultados/test_esquema_{timestamp}.xlsx'
    
    # Guardar JSON
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print(f"\n✓ JSON guardado: {json_file}")
    
    # Generar Excel
    if resultados:
        json_to_excel(json_file, excel_file)
        print(f"✓ Excel generado: {excel_file}")
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DE LA PRUEBA")
    print("="*80)
    print(f"Total URLs procesadas: {len(TEST_URLS)}")
    print(f"Exitosas: {exitosos} ({exitosos/len(TEST_URLS)*100:.1f}%)")
    print(f"Fallidas: {fallidos} ({fallidos/len(TEST_URLS)*100:.1f}%)")
    
    if resultados:
        print(f"\nColumnas en el esquema:")
        primer_resultado = resultados[0]
        columnas = list(primer_resultado.keys())
        print(f"  Total: {len(columnas)}")
        
        # Verificar campos críticos
        campos_criticos = [
            'ID Inmos', 'Inmos', 'URL INMUEBLE', 'COD FR', 'TITULO', 
            'PRECIO', 'Tipo de inmueble', 'Tipo de oferta',
            'Contrato minimo', 'Documentacion requerida', 'M² de terraza'
        ]
        print(f"\n  Campos críticos presentes:")
        for campo in campos_criticos:
            presente = '✓' if campo in columnas else '✗'
            print(f"    {presente} {campo}")
        
        # Verificar columnas de imágenes
        img_cols = [c for c in columnas if c.startswith('Imagen ')]
        print(f"\n  Columnas de imagen: {len(img_cols)}")
        
        # Mostrar muestra de datos
        print(f"\nMuestra de la primera propiedad:")
        print(f"  Tipo de inmueble: {primer_resultado.get('Tipo de inmueble')}")
        print(f"  Tipo de oferta: {primer_resultado.get('Tipo de oferta')}")
        print(f"  Precio: {primer_resultado.get('PRECIO')}")
        print(f"  Habitaciones: {primer_resultado.get('Habitaciones')}")
        print(f"  Baños: {primer_resultado.get('Baños')}")
        
        # Contar imágenes por propiedad
        total_imgs = 0
        for res in resultados:
            total_imgs += sum(1 for j in range(1, 16) if res.get(f'Imagen {j}'))
        print(f"\n  Promedio de imágenes por propiedad: {total_imgs/len(resultados):.1f}")
    
    print("\n" + "="*80)
    print("PRUEBA COMPLETADA")
    print("="*80)
    print(f"\nRevisa los archivos generados:")
    print(f"  JSON: {json_file}")
    print(f"  Excel: {excel_file}")
    print()

if __name__ == '__main__':
    main()
