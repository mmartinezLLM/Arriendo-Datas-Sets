import pandas as pd

df = pd.read_excel('resultados/properties_excel_20251124_091108.xlsx')

# Verificar columnas de imagen
img_cols = [c for c in df.columns if c.startswith('Imagen')]
print(f'Total de columnas de imagen: {len(img_cols)}')

# Ver una muestra de la primera propiedad
sample = df.iloc[0]
imgs_filled = sum(1 for col in img_cols if pd.notna(sample[col]) and sample[col] != '')
print(f'\nImágenes en la primera propiedad: {imgs_filled}')

# Mostrar primeras 3 imágenes
for i in range(1, 4):
    col = f'Imagen {i}'
    val = sample[col]
    if pd.notna(val) and val != '':
        print(f'{col}: {val[:80]}...')
    else:
        print(f'{col}: (vacía)')

# Verificar algunos de los nuevos campos
print(f'\nNuevos campos:')
print(f'Contrato minimo: {sample["Contrato minimo"]}')
print(f'Documentacion requerida: {sample["Documentacion requerida"]}')
print(f'M² de terraza: {sample["M² de terraza"]}')

# Verificar total de columnas
print(f'\nTotal de columnas: {len(df.columns)}')
print(f'Total de filas: {len(df)}')
