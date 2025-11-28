#!/usr/bin/env python3
"""
Script para diagnosticar qué número de teléfono se revela después del click
"""
import time
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def test_phone_reveal():
    # Crear driver con perfil temporal
    temp_dir = tempfile.mkdtemp()
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={temp_dir}")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        url = "https://www.fincaraiz.com.co/inmobiliarias/perfil/176359705"
        print(f"Abriendo: {url}")
        driver.get(url)
        
        print("\n1. Esperando carga inicial (5 segundos)...")
        time.sleep(5)
        
        print("\n2. Capturando HTML ANTES del click:")
        html_before = driver.page_source
        
        # Buscar todos los números en el HTML antes del click
        import re
        pattern_before = re.findall(r'\+57\d{9,}|\d{10,}', html_before)
        print(f"   Números encontrados antes del click: {set(pattern_before[:10])}")
        
        # Si está registrado, debería haber datos
        if "31828640838" in html_before:
            print("   ✓ Número antigua en el HTML: 31828640838")
        if "+573168253295" in html_before:
            print("   ✓ Número esperada ya visible: +573168253295")
        
        print("\n3. Buscando y clickeando botón 'Ver teléfono'...")
        button = driver.find_element(By.CSS_SELECTOR, "button.btn-secondary")
        print(f"   Botón encontrado: '{button.text}'")
        
        driver.execute_script("arguments[0].click();", button)
        print("   ✓ Click ejecutado")
        
        print("\n4. Esperando 4 segundos después del click...")
        time.sleep(4)
        
        print("\n5. Capturando HTML DESPUÉS del click:")
        html_after = driver.page_source
        
        # Comparar cambios
        if html_after != html_before:
            print("   ✓ HTML cambió después del click")
        else:
            print("   ⚠ HTML NO cambió después del click")
        
        # Buscar números después del click
        pattern_after = re.findall(r'\+57\d{9,}|\d{10,}', html_after)
        print(f"   Números encontrados después del click: {set(pattern_after[:10])}")
        
        # Específicamente buscar el número esperado
        if "+573168253295" in html_after:
            print("   ✓ Número esperada ENCONTRADA después del click: +573168253295")
        else:
            print("   ✗ Número esperada NO ENCONTRADA después del click")
        
        print("\n6. Buscando elemento con la clase que suele contener el teléfono...")
        try:
            # A veces el número está en un elemento específico
            phone_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '3168253295')]")
            print(f"   Elementos con teléfono 3168253295: {len(phone_elements)}")
            for elem in phone_elements:
                print(f"     - {elem.tag_name}: {elem.text[:100]}")
        except:
            pass
        
        print("\n7. Buscando el texto visible en la página...")
        body_text = driver.find_element(By.TAG_NAME, "body").text
        if "3168253295" in body_text:
            print("   ✓ Número 3168253295 está visible en el texto")
            # Extraer contexto
            idx = body_text.find("3168253295")
            print(f"   Contexto: ...{body_text[max(0,idx-50):idx+100]}...")
        else:
            print("   ✗ Número 3168253295 NO está en el texto visible")
        
        print("\n8. Guardando HTML después del click para inspección manual...")
        with open("html_after_click.html", "w", encoding="utf-8") as f:
            f.write(html_after)
        print("   HTML guardado en: html_after_click.html")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_phone_reveal()
