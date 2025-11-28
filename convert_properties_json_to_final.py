import json
import sys
import os
from datetime import datetime


def _si_no_normalizado(valor):
    if valor is None:
        return None
    v = str(valor).strip().lower()
    positivos = ['si', 'sí', 'true', '1', 'admite', 'acepta', 'permitidas', 'permitido']
    negativos = ['no', 'false', '0', 'no admite', 'no acepta', 'prohibido']
    if any(p == v or p in v for p in positivos):
        return 'Sí'
    if any(n == v or n in v for n in negativos):
        return 'No'
    if v in ['sí', 'si']:
        return 'Sí'
    if v == 'no':
        return 'No'
    return None


def _inferir_tipo_oferta(url: str, tipo_propiedad: str):
    try:
        u = (url or '').lower()
        accion = None
        if '-en-venta-' in u:
            accion = 'venta'
        elif '-en-arriendo-' in u:
            accion = 'arriendo'
        if not accion:
            return None
        # Solo devolver 'venta' o 'arriendo'; el tipo de inmueble va en otra columna
        return accion
    except Exception:
        return None


esschema_cols = [
    'ID Inmos', 'Inmos', 'URL INMUEBLE', 'COD FR', 'COD FR LEGACY', 'TITULO', 'DESCRIPCION',
    'PRECIO', 'PRECIO ADMIN', 'UBICACION', 'Tipo de inmueble', 'Tipo de oferta', 'Estado',
    'Habitaciones', 'Baños', 'Parqueaderos', 'Estrato', 'Antigüedad', 'Metros',
    'Area', 'Area privada', 'Area del terreno', 'Area lote', 'Piso No.', 'Cantidad de pisos',
    'Cantidad de ambientes', 'Apto para oficina', 'Acepta permuta', 'Remodelado', 'Penthouse',
    'Contrato minimo', 'Documentacion requerida', 'Acepta mascotas', 'M² de terraza', 'Comodidades'
]

# Agregar columnas de imágenes
for i in range(1, 16):
    esschema_cols.append(f'Imagen {i}')


def _formatear(item: dict) -> dict:
    if 'URL INMUEBLE' in item:
        # Ya final
        return {k: item.get(k) for k in esschema_cols}
    caract = item.get('caracteristicas', {}) or {}
    inmo = item.get('inmobiliaria', {}) or {}
    imagenes = item.get('imagenes', []) or []
    comodidades = item.get('comodidades', []) or []
    
    area_terreno = (
        caract.get('Área del terreno') or caract.get('Área del Terreno') or
        caract.get('Área del lote') or caract.get('Área de lote') or
        caract.get('Lote')
    )
    area_lote = caract.get('Área de lote') or caract.get('Lote')
    
    piso_n = (
        caract.get('Piso N') or caract.get('Piso N°') or 
        caract.get('Piso No.') or caract.get('Piso')
    )
    cantidad_ambientes = (
        caract.get('Cantidad de ambientes') or caract.get('Cantidad de Ambientes') or
        caract.get('Ambientes') or caract.get('N° de ambientes') or
        caract.get('Nº de ambientes') or caract.get('Numero de ambientes') or
        caract.get('Número de ambientes')
    )
    acepta_mascotas = _si_no_normalizado(
        caract.get('Acepta mascotas') or caract.get('Se aceptan mascotas') or
        caract.get('Admite mascotas') or caract.get('Mascotas') or item.get('pet_friendly')
    )
    
    metros_terraza = (
        caract.get('M² de terraza') or
        caract.get('Metros de terraza') or
        caract.get('Área de terraza') or
        caract.get('Terraza')
    )
    
    contrato_minimo = (
        caract.get('Contrato mínimo') or
        caract.get('Contrato minimo') or
        caract.get('Tiempo mínimo de contrato')
    )
    
    documentacion = (
        caract.get('Documentación requerida') or
        caract.get('Documentacion requerida') or
        caract.get('Documentos requeridos')
    )
    
    tipo_oferta = _inferir_tipo_oferta(item.get('url'), item.get('tipo_propiedad'))

    def _inferir_tipo_inmu(url: str, tipo_prop: str):
        # Intentar inferir desde la URL primero (más confiable)
        try:
            u = (url or '').lower().rstrip('/')
            partes = u.split('/')
            if len(partes) >= 2:
                slug = partes[-2]
                base = slug.split('-en-')[0] if '-en-' in slug else slug
                # Ordenados de más específico a menos específico
                mapping = {
                    'apartaestudios': 'Apartaestudio',
                    'apartaestudio': 'Apartaestudio',
                    'apartamento': 'Apartamento',
                    'casa-campestre': 'Casa campestre',
                    'casa-lote': 'Casa lote',
                    'casa': 'Casa',
                    'local': 'Local',
                    'oficina': 'Oficina',
                    'lote': 'Lote',
                    'bodega': 'Bodega',
                    'finca': 'Finca',
                    'consultorio': 'Consultorio',
                    'edificio': 'Edificio',
                    'cabaña': 'Cabaña',
                    'cabana': 'Cabaña',
                    'habitacion': 'Habitación',
                    'parqueadero': 'Parqueadero',
                }
                for clave, val in mapping.items():
                    if base.startswith(clave):
                        return val
        except Exception:
            pass
        
        # Fallback: usar tipo_propiedad si la URL no dio resultado
        if tipo_prop:
            return tipo_prop
        
        return None
    
    out = {
        'ID Inmos': inmo.get('id'),
        'Inmos': inmo.get('nombre'),
        'URL INMUEBLE': item.get('url'),
        'COD FR': item.get('codigo_fr'),
        'COD FR LEGACY': item.get('codigo_fr_legacy'),
        'TITULO': item.get('h1'),
        'DESCRIPCION': item.get('descripcion'),
        'PRECIO': item.get('precio'),
        'PRECIO ADMIN': item.get('precio_administracion'),
        'UBICACION': item.get('ubicacion'),
        'Tipo de inmueble': _inferir_tipo_inmu(item.get('url'), item.get('tipo_propiedad')),
        'Tipo de oferta': tipo_oferta,
        'Estado': caract.get('Estado'),
        'Habitaciones': item.get('habitaciones'),
        'Baños': item.get('banos'),
        'Parqueaderos': caract.get('Parqueaderos'),
        'Estrato': caract.get('Estrato'),
        'Antigüedad': caract.get('Antigüedad') or caract.get('Antiguedad'),
        'Metros': item.get('metros'),
        'Area': caract.get('Área') or caract.get('Area'),
        'Area privada': caract.get('Área Privada') or caract.get('Área privada') or caract.get('Area privada'),
        'Area del terreno': area_terreno,
        'Area lote': area_lote,
        'Piso No.': piso_n,
        'Cantidad de pisos': caract.get('Cantidad de pisos'),
        'Cantidad de ambientes': cantidad_ambientes,
        'Apto para oficina': _si_no_normalizado(caract.get('Apto para oficina')) or caract.get('Apto para oficina'),
        'Acepta permuta': _si_no_normalizado(caract.get('Acepta permuta')) or caract.get('Acepta permuta'),
        'Remodelado': _si_no_normalizado(caract.get('Remodelado')) or caract.get('Remodelado'),
        'Penthouse': _si_no_normalizado(caract.get('Penthouse')) or caract.get('Penthouse'),
        'Contrato minimo': contrato_minimo,
        'Documentacion requerida': documentacion,
        'Acepta mascotas': acepta_mascotas,
        'M² de terraza': metros_terraza,
        'Comodidades': ' | '.join([c for c in comodidades if c]) if comodidades else '',
    }
    
    # Agregar las primeras 15 imágenes en columnas separadas
    for i in range(15):
        img_key = f'Imagen {i+1}'
        out[img_key] = imagenes[i] if i < len(imagenes) else ''
    
    return out


def main():
    if len(sys.argv) < 2:
        print("Uso: python convert_properties_json_to_final.py <input_json> [output_json]")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    final = [_formatear(x) for x in data]
    if not output_path:
        base, ext = os.path.splitext(input_path)
        output_path = base + '_final.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final, f, ensure_ascii=False, indent=2)
    print(f"OK JSON final guardado en: {output_path}")


if __name__ == '__main__':
    main()
