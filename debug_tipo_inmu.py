base = 'lote'
mapping = {
    'apartamento': 'Apartamento',
    'apartaestudio': 'Apartaestudio',
    'apartaestudios': 'Apartaestudio',
    'casa': 'Casa',
    'casa-campestre': 'Casa campestre',
    'casa-lote': 'Casa lote',
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

result = None
for clave, val in mapping.items():
    print(f'Checking: "{base}".startswith("{clave}") = {base.startswith(clave)}')
    if base.startswith(clave):
        result = val
        print(f'  -> MATCH! Result: {val}')
        break

print(f'\nFinal result: {result}')
