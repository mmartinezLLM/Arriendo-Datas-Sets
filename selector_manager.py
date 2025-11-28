"""
Herramienta para actualizar y gestionar selectores
Útil cuando la estructura de fincaraiz.com.co cambia
"""
import json
import os
from logger_config import get_logger

logger = get_logger()

class SelectorManager:
    """Gestor de selectores CSS/XPath"""
    
    SELECTOR_FILE = "selectors_config.json"
    
    DEFAULT_SELECTORS = {
        "container": {
            "method": "css",
            "value": "[data-testid=\"companyCardWrapper\"], .company-card, .inmobiliaria-card",
            "description": "Contenedor de cada inmobiliaria"
        },
        "titulo": {
            "method": "css",
            "value": "h2, .company-name, [data-testid=\"companyName\"]",
            "description": "Título/Nombre de la inmobiliaria"
        },
        "correo": {
            "method": "css",
            "value": "a[href^=\"mailto:\"], .company-email, [data-testid=\"email\"]",
            "description": "Email de contacto"
        },
        "phone_button": {
            "method": "xpath",
            "value": "//button[contains(text(), 'Mostrar')] | //button[contains(text(), 'Ver')]",
            "description": "Botón para revelar teléfono"
        },
        "telefono": {
            "method": "css",
            "value": ".company-phone, [data-testid=\"phone\"], a[href^=\"tel:\"]",
            "description": "Número de teléfono"
        },
        "cantidad": {
            "method": "css",
            "value": ".property-count, [data-testid=\"propertyCount\"]",
            "description": "Cantidad de inmuebles"
        },
        "url": {
            "method": "css",
            "value": "a[href], [data-testid=\"companyLink\"]",
            "description": "URL/Link de la inmobiliaria"
        }
    }
    
    @classmethod
    def load_selectors(cls):
        """Carga selectores desde archivo o usa los defaults"""
        if os.path.exists(cls.SELECTOR_FILE):
            try:
                with open(cls.SELECTOR_FILE, 'r', encoding='utf-8') as f:
                    selectors = json.load(f)
                logger.info(f"Selectores cargados desde {cls.SELECTOR_FILE}")
                return selectors
            except Exception as e:
                logger.warning(f"Error cargando selectores: {e}. Usando defaults.")
        
        return cls.DEFAULT_SELECTORS.copy()
    
    @classmethod
    def save_selectors(cls, selectors):
        """Guarda selectores en archivo"""
        try:
            with open(cls.SELECTOR_FILE, 'w', encoding='utf-8') as f:
                json.dump(selectors, f, ensure_ascii=False, indent=2)
            logger.info(f"Selectores guardados en {cls.SELECTOR_FILE}")
            return True
        except Exception as e:
            logger.error(f"Error guardando selectores: {e}")
            return False
    
    @classmethod
    def update_selector(cls, key, method, value):
        """Actualiza un selector específico"""
        selectors = cls.load_selectors()
        
        if key not in selectors:
            logger.warning(f"Selector '{key}' no existe. Creando nuevo.")
        
        selectors[key] = {
            "method": method,
            "value": value,
            "description": selectors.get(key, {}).get("description", "")
        }
        
        cls.save_selectors(selectors)
        logger.info(f"Selector '{key}' actualizado")
    
    @classmethod
    def reset_to_defaults(cls):
        """Restaura selectores por defecto"""
        cls.save_selectors(cls.DEFAULT_SELECTORS.copy())
        logger.info("Selectores restaurados a valores por defecto")
    
    @classmethod
    def export_selectors(cls, filename=None):
        """Exporta selectores a archivo JSON"""
        if not filename:
            filename = f"selectors_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        selectors = cls.load_selectors()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(selectors, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Selectores exportados a {filename}")
        return filename
    
    @classmethod
    def import_selectors(cls, filename):
        """Importa selectores desde archivo JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                selectors = json.load(f)
            cls.save_selectors(selectors)
            logger.info(f"Selectores importados desde {filename}")
            return True
        except Exception as e:
            logger.error(f"Error importando selectores: {e}")
            return False
    
    @classmethod
    def print_selectors(cls):
        """Imprime todos los selectores de forma legible"""
        selectors = cls.load_selectors()
        
        print("\n" + "=" * 70)
        print("SELECTORES CONFIGURADOS")
        print("=" * 70)
        
        for key, selector in selectors.items():
            print(f"\n📌 {key.upper()}")
            print(f"   Descripción: {selector.get('description', 'N/A')}")
            print(f"   Método: {selector.get('method', 'N/A')}")
            print(f"   Valor: {selector.get('value', 'N/A')}")
        
        print("\n" + "=" * 70 + "\n")

def main():
    """Menú interactivo para gestionar selectores"""
    from datetime import datetime
    
    print("\n" + "=" * 70)
    print("GESTOR DE SELECTORES")
    print("=" * 70)
    
    while True:
        print("\n¿Qué deseas hacer?")
        print("1. Ver selectores actuales")
        print("2. Actualizar un selector")
        print("3. Restaurar valores por defecto")
        print("4. Exportar selectores")
        print("5. Importar selectores")
        print("6. Salir")
        
        choice = input("\nOpción (1-6): ").strip()
        
        if choice == '1':
            SelectorManager.print_selectors()
        
        elif choice == '2':
            key = input("Clave del selector: ").strip()
            method = input("Método (css/xpath): ").strip().lower()
            value = input("Valor del selector: ").strip()
            
            if method in ['css', 'xpath']:
                SelectorManager.update_selector(key, method, value)
                print("✓ Selector actualizado")
            else:
                print("❌ Método inválido")
        
        elif choice == '3':
            confirm = input("¿Restaurar selectores a valores por defecto? (S/N): ").strip().upper()
            if confirm == 'S':
                SelectorManager.reset_to_defaults()
                print("✓ Selectores restaurados")
        
        elif choice == '4':
            filename = input("Nombre del archivo (Enter para auto): ").strip()
            if not filename:
                filename = None
            SelectorManager.export_selectors(filename)
            print("✓ Selectores exportados")
        
        elif choice == '5':
            filename = input("Nombre del archivo a importar: ").strip()
            if os.path.exists(filename):
                if SelectorManager.import_selectors(filename):
                    print("✓ Selectores importados")
                else:
                    print("❌ Error importando selectores")
            else:
                print(f"❌ Archivo no encontrado: {filename}")
        
        elif choice == '6':
            print("¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    from datetime import datetime
    main()
