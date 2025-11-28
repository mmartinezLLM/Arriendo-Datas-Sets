#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Muestra un resumen de los datos extraídos
"""
import json
import sys

def mostrar_resumen(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    print(f"\n{'='*80}")
    print(f"RESUMEN DE EXTRACCIÓN - {len(datos)} inmuebles")
    print(f"{'='*80}\n")
    
    for i, prop in enumerate(datos[:3], 1):  # Mostrar solo los primeros 3
        print(f"INMUEBLE {i}:")
        print(f"  ID Inmos: {prop.get('id_inmos')}")
        print(f"  Inmobiliaria: {prop.get('inmos')}")
        print(f"  Código FR: {prop.get('cod_fr')}")
        print(f"  Código Legacy: {prop.get('cod_fr_legacy')}")
        print(f"  Título: {prop.get('titulo')[:60]}...")
        print(f"  Tipo Inmueble: {prop.get('tipo_inmueble')}")
        print(f"  Tipo Oferta: {prop.get('tipo_oferta')}")
        print(f"  Estado: {prop.get('estado')}")
        print(f"  Ubicación: {prop.get('ubicacion')}")
        print(f"  Precio: ${prop.get('precio'):,}" if prop.get('precio') else "  Precio: N/A")
        print(f"  Habitaciones: {prop.get('habitaciones')}")
        print(f"  Baños: {prop.get('banos')}")
        print(f"  Parqueaderos: {prop.get('parqueaderos')}")
        print(f"  Estrato: {prop.get('estrato')}")
        print(f"  Antigüedad: {prop.get('antiguedad')}")
        print(f"  Metros: {prop.get('metros')}")
        print(f"  Área: {prop.get('area')}")
        print(f"  Área Privada: {prop.get('area_privada')}")
        print(f"  Imágenes: {len(prop.get('imagenes', []))} imágenes")
        print(f"  Comodidades: {len(prop.get('comodidades', '').split('|')) if prop.get('comodidades') else 0} comodidades")
        print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python resumen_extraccion.py <archivo.json>")
        sys.exit(1)
    
    mostrar_resumen(sys.argv[1])
