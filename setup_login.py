#!/usr/bin/env python3
"""
Script para hacer login automático en fincaraiz.com.co
y guardar la sesión para uso futuro
"""
import time
import tempfile
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Credenciales
EMAIL = "juanchodiaz202025@outlook.com"
PASSWORD = "juanshocabasho23"

def login_fincaraiz():
    """
    Hace login en fincaraiz.com.co y guarda la sesión
    """
    
    # Crear directorio para el perfil persistente
    profile_dir = os.path.join(os.path.expanduser("~"), ".fincaraiz_profile")
    os.makedirs(profile_dir, exist_ok=True)
    
    print(f"Usando perfil en: {profile_dir}")
    print("=" * 70)
    
    # Configurar opciones de Chrome
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={profile_dir}")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    # options.add_argument("--headless")  # Comentado para ver lo que pasa
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        print("\n[1/5] Abriendo perfil de prueba (para encontrar login desde ahí)...")
        # Ir al perfil primero, como dijiste
        test_url = "https://www.fincaraiz.com.co/inmobiliarias/perfil/176359705"
        driver.get(test_url)
        time.sleep(3)
        
        print("[2/5] Buscando botón de login en la página...")
        wait = WebDriverWait(driver, 10)
        
        # Buscar un enlace o botón que diga "Login", "Iniciar sesión", "Ingresar", etc.
        # Primero intentar encontrar el botón de login
        try:
            # Intentar varios selectores comunes
            login_selectors = [
                "//a[contains(text(), 'Iniciar sesión')]",
                "//button[contains(text(), 'Iniciar sesión')]",
                "//a[contains(text(), 'Login')]",
                "//button[contains(text(), 'Login')]",
                "//a[contains(text(), 'Ingresar')]",
                "//a[contains(text(), 'INGRESAR')]",
                "[data-testid='login-button']",
                ".login-btn",
                "#login-btn",
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    if selector.startswith("//"):
                        login_button = driver.find_element(By.XPATH, selector)
                    elif selector.startswith("."):
                        login_button = driver.find_element(By.CSS_SELECTOR, selector)
                    elif selector.startswith("#"):
                        login_button = driver.find_element(By.CSS_SELECTOR, selector)
                    else:
                        login_button = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if login_button:
                        print(f"  ✓ Encontrado botón de login: {selector}")
                        break
                except:
                    continue
            
            if login_button:
                driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
                time.sleep(0.5)
                login_button.click()
                print("  ✓ Botón de login clickeado")
                time.sleep(3)
            else:
                print("  ⚠ No se encontró botón de login en el perfil")
                print("  Intentando acceso directo a página de login...")
                driver.get("https://www.fincaraiz.com.co/login")
                time.sleep(3)
        
        except Exception as e:
            print(f"  Error buscando login: {e}")
            print("  Intentando acceso directo a página de login...")
            driver.get("https://www.fincaraiz.com.co/login")
            time.sleep(3)
        
        print("\n[3/5] Ingresando credenciales...")
        
        # Buscar campo de email
        try:
            email_field = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='email' or @name='email' or @id='email']"))
            )
            email_field.clear()
            email_field.send_keys(EMAIL)
            print(f"  ✓ Email ingresado: {EMAIL}")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ Error ingresando email: {e}")
            
            # Intentar buscar de otra forma
            try:
                inputs = driver.find_elements(By.TAG_NAME, "input")
                print(f"  Encontrados {len(inputs)} campos de entrada:")
                for idx, inp in enumerate(inputs[:5]):
                    inp_type = inp.get_attribute("type")
                    inp_name = inp.get_attribute("name")
                    inp_placeholder = inp.get_attribute("placeholder")
                    print(f"    [{idx}] type={inp_type}, name={inp_name}, placeholder={inp_placeholder}")
            except:
                pass
            raise
        
        # Buscar campo de contraseña
        try:
            # Esperar un poco después de llenar email (a veces requiere validación)
            time.sleep(1)
            
            # A veces la contraseña viene después de presionar Tab o Enter
            email_field.send_keys("\t")
            time.sleep(0.5)
            
            password_field = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='password' or @name='password' or @id='password']"))
            )
            password_field.clear()
            password_field.send_keys(PASSWORD)
            print(f"  ✓ Contraseña ingresada")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ Error ingresando contraseña: {e}")
            raise
        
        print("\n[4/5] Enviando formulario de login...")
        
        try:
            # Buscar botón de envío
            submit_selectors = [
                "//button[contains(text(), 'Ingresar')]",
                "//button[contains(text(), 'Iniciar sesión')]",
                "//button[contains(text(), 'Login')]",
                "//button[@type='submit']",
                "//input[@type='submit']",
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = driver.find_element(By.XPATH, selector)
                    if submit_button:
                        print(f"  ✓ Botón encontrado: {selector}")
                        break
                except:
                    continue
            
            if submit_button:
                driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                time.sleep(0.5)
                submit_button.click()
                print("  ✓ Formulario enviado")
            else:
                print("  ⚠ Botón submit no encontrado, intentando presionar Enter...")
                password_field.send_keys("\n")
            
            # Esperar a que se complete el login (redirección)
            print("  Esperando procesamiento del login (10 segundos)...")
            time.sleep(10)
        
        except Exception as e:
            print(f"  ✗ Error en submit: {e}")
            raise
        
        print("\n[5/5] Verificando si el login fue exitoso...")
        
        # Verificar que estemos loguados
        current_url = driver.current_url
        print(f"  URL actual: {current_url}")
        
        page_source = driver.page_source.lower()
        
        # Indicadores de login exitoso
        login_success_indicators = [
            "logout" in page_source,
            "mi cuenta" in page_source,
            "mi perfil" in page_source,
            "cerrar sesión" in page_source,
            "datos personales" in page_source,
        ]
        
        if any(login_success_indicators):
            print("  ✓ ✓ ✓ LOGIN EXITOSO ✓ ✓ ✓")
        else:
            print("  ⚠ No se encontraron indicadores de login exitoso")
            print("  Revisando página actual...")
            print(f"  Título: {driver.title}")
        
        # Navegar a un perfil de prueba
        print("\n[BONUS] Probando acceso a perfil de inmobiliaria...")
        test_url = "https://www.fincaraiz.com.co/inmobiliarias/perfil/176359705"
        driver.get(test_url)
        time.sleep(5)
        
        html = driver.page_source
        
        # Buscar números de teléfono
        import re
        if "3168253295" in html:
            print("  ✓ ¡Se ve el número de teléfono ESPERADO!")
        else:
            numbers = re.findall(r'\+57\d{9,}|\d{9,}', html)
            print(f"  Números encontrados: {set(list(numbers)[:5])}")
        
        # Buscar si el botón existe
        try:
            button = driver.find_element(By.CSS_SELECTOR, "button.btn-secondary")
            print(f"  ✓ Botón 'Ver teléfono' encontrado")
        except:
            print(f"  ⚠ Botón 'Ver teléfono' NO encontrado")
        
        print("\n" + "=" * 70)
        print("✓ Perfil guardado en:", profile_dir)
        print("✓ Puedes cerrar el navegador ahora")
        print("=" * 70)
        
        # Esperar a que el usuario lo vea
        input("\nPresiona ENTER para cerrar el navegador...")
        
    except Exception as e:
        print(f"\n✗ Error durante el login: {type(e).__name__}: {e}")
        print("\nPor favor, verifica:")
        print("  1. Las credenciales sean correctas")
        print("  2. Tu conexión a internet funcione")
        print("  3. El sitio de fincaraiz esté disponible")
        
        input("\nPresiona ENTER para cerrar el navegador...")
    
    finally:
        driver.quit()
        print("\nNavegador cerrado.")

if __name__ == "__main__":
    login_fincaraiz()
