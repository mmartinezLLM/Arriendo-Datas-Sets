"""
Prueba específica para verificar la detección correcta del tipo de inmueble
URL problemática: https://www.fincaraiz.com.co/lote-en-venta-en-barbosa/191711457
"""
from property_crawler_selenium import PropertyCrawlerSelenium, _formatear_salida_final

# URL del lote que se detectaba mal
url_lote = "https://www.fincaraiz.com.co/lote-en-venta-en-barbosa/191711457"

print("="*80)
print("PRUEBA DE DETECCIÓN DE TIPO DE INMUEBLE")
print("="*80)
print(f"\nURL: {url_lote}")
print("\nEsperado: Lote")
print()

# Inicializar crawler
crawler = PropertyCrawlerSelenium()

# Extraer
datos_raw = crawler.extraer_propiedad(url_lote)

if datos_raw and datos_raw.get('codigo_fr'):
    print(f"\nDatos raw extraídos:")
    print(f"  tipo_propiedad (raw): {datos_raw.get('tipo_propiedad')}")
    
    # Formatear
    datos_final = _formatear_salida_final(datos_raw)
    
    print(f"\nDatos finales:")
    print(f"  Tipo de inmueble: {datos_final.get('Tipo de inmueble')}")
    print(f"  Tipo de oferta: {datos_final.get('Tipo de oferta')}")
    print(f"  Título: {datos_final.get('TITULO')}")
    print(f"  Precio: {datos_final.get('PRECIO')}")
    
    # Verificar
    if datos_final.get('Tipo de inmueble') == 'Lote':
        print("\n✅ CORRECTO: Tipo de inmueble detectado correctamente como 'Lote'")
    else:
        print(f"\n❌ ERROR: Se esperaba 'Lote' pero se obtuvo '{datos_final.get('Tipo de inmueble')}'")
else:
    print("❌ ERROR: No se pudo extraer la propiedad")

crawler.close()
print()
