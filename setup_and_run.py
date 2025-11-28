"""
Script de instalación y prueba del scraper
"""
import subprocess
import sys
import os

def install_requirements():
    """Instala las dependencias necesarias"""
    print("=" * 70)
    print("INSTALANDO DEPENDENCIAS...")
    print("=" * 70)
    
    try:
        requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
        print("\n✓ Dependencias instaladas exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error instalando dependencias: {e}")
        return False

def run_inspector():
    """Ejecuta el inspector de selectores"""
    print("\n" + "=" * 70)
    print("EJECUTANDO INSPECTOR DE SELECTORES...")
    print("=" * 70)
    print("\nEsto abrirá una ventana del navegador y analizará la estructura de la página.")
    print("Por favor, espera a que complete el análisis.\n")
    
    try:
        subprocess.call([sys.executable, 'selector_inspector.py'])
    except Exception as e:
        print(f"Error ejecutando inspector: {e}")

def run_scraper():
    """Ejecuta el scraper principal"""
    print("\n" + "=" * 70)
    print("EJECUTANDO SCRAPER PRINCIPAL...")
    print("=" * 70)
    print("\nEsto extraerá la información de las inmobiliarias.")
    print("Por favor, espera a que complete la extracción.\n")
    
    try:
        subprocess.call([sys.executable, 'main_fincaraiz.py'])
    except Exception as e:
        print(f"Error ejecutando scraper: {e}")

def main():
    """Menú principal"""
    print("\n" + "=" * 70)
    print("SCRAPER DE INMOBILIARIAS - FINCARAIZ.COM.CO")
    print("=" * 70)
    
    while True:
        print("\n¿Qué deseas hacer?")
        print("1. Instalar dependencias")
        print("2. Inspeccionar estructura de la página")
        print("3. Ejecutar scraper")
        print("4. Salir")
        
        choice = input("\nOpción (1-4): ").strip()
        
        if choice == '1':
            if install_requirements():
                print("Ahora puedes ejecutar el scraper.")
        elif choice == '2':
            run_inspector()
        elif choice == '3':
            run_scraper()
        elif choice == '4':
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")

if __name__ == "__main__":
    main()
