#!/usr/bin/env python3
"""
Script para conectarse a Chrome existente (si está abierta)
"""
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Path a tu Chrome User Data
user_data_path = r"C:\Users\Miguel Martinez SSD\AppData\Local\Google\Chrome\User Data"

print(f"Buscando Chrome User Data en: {user_data_path}")
print(f"¿Existe el directorio? {os.path.exists(user_data_path)}")

if not os.path.exists(user_data_path):
    print("ERROR: No se encontró el directorio de Chrome User Data")
    print("Asegúrate de cerrar Chrome completamente antes de ejecutar esto.")
    exit(1)

# IMPORTANTE: Debes cerrar Chrome completamente antes de esto
print("\n⚠ IMPORTANTE: Debes cerrar Chrome completamente ANTES de ejecutar este script")
print("  (porque Chrome no permite múltiples instancias con el mismo perfil)")
print("\nIntentando conectar con tu perfil de Chrome...")

try:
    options = webdriver.ChromeOptions()
    # NO usar --user-data-dir directamente - usar el perfil "Default"
    options.add_argument(f"user-data-dir={user_data_path}")
    # O intentar con un perfil específico
    # options.add_argument("--profile-directory=Default")
    
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    print("\n✓ Conectado a Chrome")
    
    url = "https://www.fincaraiz.com.co/inmobiliarias/perfil/176359705"
    print(f"\nAbriendo: {url}")
    driver.get(url)
    time.sleep(5)
    
    # Verificar si estamos loguados (buscar indicadores de login)
    page_source = driver.page_source
    
    if "logout" in page_source.lower() or "mi cuenta" in page_source.lower():
        print("\n✓ Parece que ESTÁS LOGUADO en fincaraiz")
    else:
        print("\n✗ No parece que estés loguado")
    
    # Buscar el número
    if "3168253295" in page_source:
        print("✓ ¡El número correcto ESTÁ EN el HTML!")
    else:
        print("✗ El número correcto no está en el HTML")
    
    # Ver el título
    title = driver.title
    print(f"\nTítulo de la página: {title}")
    
    # Buscar el botón
    try:
        button = driver.find_element(By.CSS_SELECTOR, "button.btn-secondary")
        print(f"✓ Botón 'Ver teléfono' encontrado: {button.text}")
    except:
        print("✗ Botón 'Ver teléfono' no encontrado")
    
    input("\nPresiona ENTER para cerrar el navegador...")
    driver.quit()
    
except Exception as e:
    print(f"\n✗ Error: {type(e).__name__}: {e}")
    print("\nPosibles causas:")
    print("  1. Chrome no está completamente cerrado")
    print("  2. Otro proceso está usando el perfil")
    print("  3. El perfil está bloqueado")
    print("\nSolución: Cierra Chrome completamente y vuelve a intentar")
