#!/usr/bin/env python3
"""
Script simplificado: abre el perfil y te permite hacer login MANUALMENTE
Luego guarda la sesión para uso futuro
"""
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Credenciales (para referencia)
EMAIL = "juanchodiaz202025@outlook.com"
PASSWORD = "juanshocabasho23"

def setup_manual_login():
    """
    Abre Chrome, va al perfil, y te permite hacer login manualmente
    """
    
    # Crear directorio para el perfil persistente
    profile_dir = os.path.join(os.path.expanduser("~"), ".fincaraiz_profile")
    os.makedirs(profile_dir, exist_ok=True)
    
    print("=" * 70)
    print("CONFIGURACIÓN DE LOGIN PARA FINCARAIZ.COM.CO")
    print("=" * 70)
    print(f"\nPerfil guardado en: {profile_dir}")
    print("\nCredenciales:")
    print(f"  Email: {EMAIL}")
    print(f"  Password: {PASSWORD}")
    print("\n" + "=" * 70)
    
    # Configurar Chrome
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={profile_dir}")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Paso 1: Ir al perfil de prueba
        test_url = "https://www.fincaraiz.com.co/inmobiliarias/perfil/176359705"
        print(f"\n[PASO 1] Abriendo perfil de prueba...")
        print(f"URL: {test_url}")
        driver.get(test_url)
        time.sleep(3)
        
        print("\n[PASO 2] Analizando página...")
        
        # Mostrar todos los enlaces que podrían ser el login
        all_links = driver.find_elements(By.TAG_NAME, "a")
        print(f"\nEnlaces en la página (primeros 20):")
        for idx, link in enumerate(all_links[:20]):
            text = link.text.strip()[:50]
            href = link.get_attribute('href')
            if text or (href and 'login' in href.lower()):
                print(f"  [{idx}] {text} -> {href}")
        
        # Mostrar botones
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\nBotones en la página:")
        for idx, btn in enumerate(all_buttons[:15]):
            text = btn.text.strip()[:50]
            btn_class = btn.get_attribute('class')
            print(f"  [{idx}] {text} | class='{btn_class}'")
        
        print("\n" + "=" * 70)
        print("INSTRUCCIONES:")
        print("=" * 70)
        print("1. En el navegador que se acaba de abrir, busca el botón/enlace de LOGIN")
        print("2. Haz click y completa el login con tus credenciales:")
        print(f"   Email: {EMAIL}")
        print(f"   Password: {PASSWORD}")
        print("3. Una vez loguado, vuelve a esta ventana de terminal")
        print("4. Presiona ENTER para verificar que el login funcionó")
        print("=" * 70)
        
        input("\n>>> Presiona ENTER cuando hayas completado el login...")
        
        # Verificar si el login funcionó
        print("\n[PASO 3] Verificando login...")
        
        # Recargar la página del perfil
        driver.get(test_url)
        time.sleep(3)
        
        html = driver.page_source.lower()
        
        # Buscar indicadores de login exitoso
        if any(x in html for x in ['logout', 'cerrar sesión', 'mi cuenta', 'mi perfil']):
            print("  ✓ ¡Login exitoso! Se detectan indicadores de sesión activa")
        else:
            print("  ⚠ No se detectan indicadores claros de login")
        
        # Buscar el número de teléfono esperado
        if "3168253295" in driver.page_source:
            print("  ✓ ✓ ✓ ¡ÉXITO! El número de teléfono esperado ES VISIBLE")
            print("  Esto confirma que el login funcionó correctamente")
        else:
            print("  ⚠ El número esperado no está visible aún")
            
            # Intentar hacer click en "Ver teléfono"
            try:
                button = driver.find_element(By.CSS_SELECTOR, "button.btn-secondary")
                print(f"  Encontrado botón: '{button.text}'")
                print("  Haciendo click...")
                driver.execute_script("arguments[0].click();", button)
                time.sleep(4)
                
                if "3168253295" in driver.page_source:
                    print("  ✓ ✓ ✓ Después del click: ¡Número visible!")
                else:
                    print("  ⚠ Aún no se ve el número esperado")
            except Exception as e:
                print(f"  Error intentando click: {e}")
        
        print("\n" + "=" * 70)
        print("SESIÓN GUARDADA")
        print("=" * 70)
        print(f"Perfil guardado en: {profile_dir}")
        print("\nAhora puedes usar este perfil en tus scripts de extracción")
        print("Para ello, usa: user-data-dir=" + profile_dir)
        print("=" * 70)
        
        input("\nPresiona ENTER para cerrar el navegador...")
        
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        
        input("\nPresiona ENTER para cerrar el navegador...")
    
    finally:
        driver.quit()
        print("\n✓ Navegador cerrado. Sesión guardada en el perfil.")

if __name__ == "__main__":
    setup_manual_login()
