import os
import json
import csv
import pandas as pd

def unir_json_a_csv_y_excel(directorio_json, archivo_csv, archivo_excel):
    import re
    def limpiar_excel(texto):
        if not isinstance(texto, str):
            return texto
        # Eliminar caracteres no permitidos por el Ecel
        return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', texto)
    # Buscar todos los archivos JSON en las carpetas desde el lote1 al lote5
    columnas_ordenadas = [
        'Id Inmos', 'Inmos', 'URL INMUEBLE', 'COD FR', 'COD FR LEGACY', 'TITULO', 'DESCRIPCION', 'PRECIO', 'PRECIO ADMIN', 'UBICACION',
        'Tipo de inmueble', 'Tipo de oferta', 'Estado', 'Habitaciones', 'Baños', 'Parqueaderos', 'Estrato', 'Antigüedad',
        'Metros', 'Area', 'Area privada', 'Area del terreno', 'Area lote', 'Piso No.', 'Cantidad de pisos', 'Cantidad de ambientes',
        'Apto para oficina', 'Acepta permuta', 'Remodelado', 'Penthouse', 'Contrato minimo', 'Documentacion requerida',
        'Acepta mascotas', 'M² de terraza', 'Comodidades',
        'Imagen 1', 'Imagen 2', 'Imagen 3', 'Imagen 4', 'Imagen 5', 'Imagen 6', 'Imagen 7', 'Imagen 8', 'Imagen 9', 'Imagen 10',
        'Imagen 11', 'Imagen 12', 'Imagen 13', 'Imagen 14', 'Imagen 15'
    ]
    mapeo = {
        'Id Inmos': 'id_inmos',
        'Inmos': 'inmos',
        'URL INMUEBLE': 'url_inmueble',
        'COD FR': 'cod_fr',
        'COD FR LEGACY': 'cod_fr_legacy',
        'TITULO': 'titulo',
        'DESCRIPCION': 'descripcion',
        'PRECIO': 'precio',
        'PRECIO ADMIN': 'precio_admin',
        'UBICACION': 'ubicacion',
        'Tipo de inmueble': 'tipo_inmueble',
        'Tipo de oferta': 'tipo_oferta',
        'Estado': 'estado',
        'Habitaciones': 'habitaciones',
        'Baños': 'banos',
        'Parqueaderos': 'parqueaderos',
        'Estrato': 'estrato',
        'Antigüedad': 'antiguedad',
        'Metros': 'metros',
        'Area': 'area',
        'Area privada': 'area_privada',
        'Area del terreno': 'area_del_terreno',
        'Area lote': 'area_lote',
        'Piso No.': 'piso_no',
        'Cantidad de pisos': 'cantidad_de_pisos',
        'Cantidad de ambientes': 'cantidad_de_ambientes',
        'Apto para oficina': 'apto_para_oficina',
        'Acepta permuta': 'acepta_permuta',
        'Remodelado': 'remodelado',
        'Penthouse': 'penthouse',
        'Contrato minimo': 'contrato_minimo',
        'Documentacion requerida': 'documentacion_requerida',
        'Acepta mascotas': 'acepta_mascotas',
        'M² de terraza': 'm2_de_terraza',
        'Comodidades': 'comodidades',
        'Imagen 1': 'imagen_1',
        'Imagen 2': 'imagen_2',
        'Imagen 3': 'imagen_3',
        'Imagen 4': 'imagen_4',
        'Imagen 5': 'imagen_5',
        'Imagen 6': 'imagen_6',
        'Imagen 7': 'imagen_7',
        'Imagen 8': 'imagen_8',
        'Imagen 9': 'imagen_9',
        'Imagen 10': 'imagen_10',
        'Imagen 11': 'imagen_11',
        'Imagen 12': 'imagen_12',
        'Imagen 13': 'imagen_13',
        'Imagen 14': 'imagen_14',
        'Imagen 15': 'imagen_15',
    }
    # Escribir CSV directamente registro a registro
    with open(archivo_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columnas_ordenadas, extrasaction='ignore')
        writer.writeheader()
        total_registros = 0
        for subcarpeta in os.listdir(directorio_json):
            if subcarpeta.startswith('lote_0') and os.path.isdir(os.path.join(directorio_json, subcarpeta)):
                ruta_subcarpeta = os.path.join(directorio_json, subcarpeta)
                archivos_json = [file for file in os.listdir(ruta_subcarpeta) if file.endswith('.json')]
                for archivo in archivos_json:
                    ruta = os.path.join(ruta_subcarpeta, archivo)
                    print(f"Procesando archivo: {ruta}")
                    try:
                        with open(ruta, 'r', encoding='utf-8') as fjson:
                            contenido = json.load(fjson)
                            registros = contenido if isinstance(contenido, list) else [contenido]
                            for item in registros:
                                fila = {col: item.get(mapeo[col], '') for col in columnas_ordenadas}
                                imagenes = item.get('imagenes', [])
                                if not isinstance(imagenes, list):
                                    imagenes = []
                                for i in range(15):
                                    col_img = f'Imagen {i+1}'
                                    fila[col_img] = imagenes[i] if i < len(imagenes) else ''
                                # Limpiar caracteres especiales en cada celda antes de escribir
                                for k in fila:
                                    fila[k] = limpiar_excel(fila[k])
                                writer.writerow(fila)
                                total_registros += 1
                    except Exception as e:
                        print(f"Error leyendo {archivo}: {e}")
        if total_registros == 0:
            print("No se encontraron datos para procesar.")
            return
    print(f"CSV generado: {archivo_csv} con {total_registros} registros.")

    df = pd.read_csv(archivo_csv)
    df = df[columnas_ordenadas]
    df.to_excel(archivo_excel, index=False)
    print(f"Excel generado: {archivo_excel}")

# Auf Die Knie Blue Lock

if __name__ == "__main__":
    directorio_json = os.path.dirname(os.path.abspath(__file__))
    archivo_csv = os.path.join(directorio_json, 'unidos.csv')
    archivo_excel = os.path.join(directorio_json, 'unidos.xlsx')
    unir_json_a_csv_y_excel(directorio_json, archivo_csv, archivo_excel)