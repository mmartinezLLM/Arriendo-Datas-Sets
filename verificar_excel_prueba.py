import pandas as pd

df = pd.read_excel('resultados/test_esquema_20251124_092116.xlsx')

print('='*80)
print('VERIFICACIÓN DEL EXCEL GENERADO')
print('='*80)

print('\nColumnas (primeras 35):')
for i, col in enumerate(df.columns[:35], 1):
    print(f'{i:2d}. {col}')

print(f'\n... y {len(df.columns)-35} columnas más (imágenes)')

print(f'\nTotal columnas: {len(df.columns)}')
print(f'Total filas: {len(df)}')

# Verificar las columnas de imágenes
img_cols = [c for c in df.columns if c.startswith('Imagen ')]
print(f'\nColumnas de imagen: {img_cols}')

# Ver datos de la primera fila
print('\n' + '='*80)
print('MUESTRA DE DATOS - Primera Propiedad')
print('='*80)
row = df.iloc[0]
print(f"Tipo de inmueble: {row['Tipo de inmueble']}")
print(f"Tipo de oferta: {row['Tipo de oferta']}")
print(f"Título: {row['TITULO']}")
print(f"Precio: ${row['PRECIO']:,.0f}")
print(f"Ubicación: {row['UBICACION']}")
print(f"Habitaciones: {row['Habitaciones']}")
print(f"Baños: {row['Baños']}")
print(f"Metros: {row['Metros']}")

# Contar imágenes llenas
imgs = sum(1 for col in img_cols if pd.notna(row[col]) and row[col] != '')
print(f"Imágenes: {imgs}/15")

# Ver nuevos campos
print('\n' + '='*80)
print('NUEVOS CAMPOS')
print('='*80)
print(f"Contrato minimo: {row['Contrato minimo']}")
print(f"Documentacion requerida: {row['Documentacion requerida']}")
print(f"M² de terraza: {row['M² de terraza']}")

# Ver algunas comodidades
print('\n' + '='*80)
print('COMODIDADES')
print('='*80)
if pd.notna(row['Comodidades']) and row['Comodidades']:
    comodidades = str(row['Comodidades']).split(' | ')
    print(f"Total: {len(comodidades)}")
    print(f"Primeras 5: {' | '.join(comodidades[:5])}")
else:
    print("Sin comodidades")
