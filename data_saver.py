"""
Guardador de datos en diferentes formatos
"""
import csv
import json
import pandas as pd
from datetime import datetime
import os
from config import OUTPUT_DIR, OUTPUT_FORMAT
from logger_config import get_logger

logger = get_logger()

class DataSaver:
    """Gestor de guardado de datos"""
    
    def __init__(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def save_data(self, data, filename=None):
        """Guarda los datos en el formato configurado"""
        if not filename:
            filename = f"inmobiliarias_{self.timestamp}"
        
        try:
            if OUTPUT_FORMAT.lower() == "csv":
                return self._save_csv(data, filename)
            elif OUTPUT_FORMAT.lower() == "json":
                return self._save_json(data, filename)
            elif OUTPUT_FORMAT.lower() == "excel":
                return self._save_excel(data, filename)
            else:
                logger.error(f"Formato no soportado: {OUTPUT_FORMAT}")
                return None
        
        except Exception as e:
            logger.error(f"Error guardando datos: {str(e)}")
            return None
    
    def _save_csv(self, data, filename):
        """Guarda datos en formato CSV"""
        try:
            filepath = os.path.join(OUTPUT_DIR, f"{filename}.csv")
            
            if not data:
                logger.warning("No hay datos para guardar en CSV")
                return None
            
            # Usar pandas para mejor manejo
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            logger.info(f"Datos guardados en CSV: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Error guardando CSV: {str(e)}")
            return None
    
    def _save_json(self, data, filename):
        """Guarda datos en formato JSON"""
        try:
            filepath = os.path.join(OUTPUT_DIR, f"{filename}.json")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Datos guardados en JSON: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Error guardando JSON: {str(e)}")
            return None
    
    def _save_excel(self, data, filename):
        """Guarda datos en formato Excel"""
        try:
            filepath = os.path.join(OUTPUT_DIR, f"{filename}.xlsx")
            
            if not data:
                logger.warning("No hay datos para guardar en Excel")
                return None
            
            df = pd.DataFrame(data)
            
            # Crear writer de Excel con formato
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Inmobiliarias')
                
                # Ajustar ancho de columnas
                worksheet = writer.sheets['Inmobiliarias']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(cell.value)
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            logger.info(f"Datos guardados en Excel: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Error guardando Excel: {str(e)}")
            return None
    
    def get_summary(self, data):
        """Obtiene un resumen de los datos extraídos"""
        try:
            if not data:
                return "No hay datos para resumir"
            
            summary = {
                'total_inmobiliarias': len(data),
                'con_telefono': len([d for d in data if d.get('telefono') and d.get('telefono') != "No disponible"]),
                'con_correo': len([d for d in data if d.get('correo') and d.get('correo') != "No disponible"]),
                'total_inmuebles': sum(d.get('cantidad_inmuebles', 0) for d in data),
                'timestamp': datetime.now().isoformat()
            }
            
            return summary
        
        except Exception as e:
            logger.error(f"Error generando resumen: {str(e)}")
            return None
