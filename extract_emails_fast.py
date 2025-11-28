"""
extract_emails_fast.py - Extrae emails y teléfonos de perfil de inmobiliarias
Usa Selenium para interactuar con elementos que requieren click
"""
import argparse
import json
import os
import re
import time
from datetime import datetime
import tempfile

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

RESULTS_DIR = 'resultados'
os.makedirs(RESULTS_DIR, exist_ok=True)

def extract_contact_info(url, driver=None, wait=None):
    """
    Extrae email y teléfono de una página de perfil de inmobiliaria.
    """
    email = None
    telefono = None
    
    try:
        # Navegar a la URL
        driver.get(url)
        time.sleep(0)
        
        # Esperar a que cargue el contenido principal
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))
        
        # Buscar email
        try:
            # Email puede estar en un atributo href o texto visible
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', driver.page_source)
            if email_match:
                email = email_match.group(0)
        except Exception as e:
            pass
        
        # Buscar teléfono - hacer click en botón primero
        print(f"  Esperando carga completa de la página (1 segundo)...")
        time.sleep(1)
        
        # Scroll hacia el centro para asegurar que los elementos estén visibles
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        time.sleep(0.5)
        
        print(f"  Buscando botón 'Ver teléfono'...")
        button_found = False
        button = None
        
        # DIAGNÓSTICO: Ver qué hay en la página
        try:
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            print(f"  [DEBUG] Total botones en página: {len(all_buttons)}")
            for idx, btn in enumerate(all_buttons[:15]):
                btn_text = btn.text[:60] if btn.text else "(sin texto)"
                btn_class = btn.get_attribute('class')
                print(f"    Button {idx}: class='{btn_class}' | text='{btn_text}'")
        except:
            pass
        
        # ESTRATEGIA 1: CSS Selector directo (más rápido)
        try:
            print(f"  - Intentando CSS selector 'button.btn-secondary'...")
            button = driver.find_element(By.CSS_SELECTOR, "button.btn-secondary")
            print(f"    ✓ Encontrado botón: '{button.text}'")
            
            # Scroll y click por JavaScript
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", button)
            print(f"    ✓ Click ejecutado por JavaScript. Esperando 1.6 segundos...")
            time.sleep(1.6)
            button_found = True
        except Exception as e:
            print(f"    ✗ Falló: {type(e).__name__}")
        
        # ESTRATEGIA 2: XPath con 'Ver teléfono'
        if not button_found:
            try:
                print(f"  - Intentando XPath '//button[contains(., \"Ver teléfono\")]'...")
                button = driver.find_element(By.XPATH, "//button[contains(., 'Ver teléfono')]")
                print(f"    ✓ Encontrado botón: '{button.text}'")
                
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(0.3)
                driver.execute_script("arguments[0].click();", button)
                print(f"    ✓ Click ejecutado. Esperando 1.6 segundos...")
                time.sleep(1.6)
                button_found = True
            except Exception as e:
                print(f"    ✗ Falló: {type(e).__name__}")
        
        # ESTRATEGIA 3: Iterar todos los botones manualmente
        if not button_found:
            try:
                print(f"  - Buscando manualmente en todos los botones...")
                buttons = driver.find_elements(By.TAG_NAME, "button")
                
                for idx, button in enumerate(buttons):
                    btn_text = button.text.lower()
                    if ("ver" in btn_text or "teléfono" in btn_text or "telefono" in btn_text) and button.is_displayed():
                        print(f"    ✓ Botón {idx} coincide: '{button.text}'")
                        
                        driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(0.3)
                        driver.execute_script("arguments[0].click();", button)
                        print(f"    ✓ Click ejecutado. Esperando 1.6 segundos...")
                        time.sleep(1.6)
                        button_found = True
                        break
            except Exception as e:
                print(f"    ✗ Falló: {type(e).__name__}: {e}")
        
        # ESTRATEGIA 4: Script JavaScript puro
        if not button_found:
            try:
                print(f"  - Ejecutando script JavaScript puro...")
                result = driver.execute_script("""
                    var found = false;
                    var buttons = document.querySelectorAll('button');
                    console.log('Total botones: ' + buttons.length);
                    for(var i = 0; i < buttons.length; i++) {
                        var txt = buttons[i].textContent.toLowerCase();
                        console.log('Button ' + i + ': ' + buttons[i].textContent.substring(0, 50));
                        if((txt.includes('ver') || txt.includes('teléfono') || txt.includes('telefono')) && txt.includes('teléfono') || txt.includes('telefono')) {
                            console.log('ENCONTRADO: ' + buttons[i].textContent);
                            buttons[i].scrollIntoView(true);
                            buttons[i].click();
                            found = true;
                            break;
                        }
                    }
                    return found;
                """)
                if result:
                    print(f"    ✓ Script encontró y clickeó botón. Esperando 1.6 segundos...")
                    time.sleep(1.6)
                    button_found = True
                else:
                    print(f"    ✗ Script no encontró botón coincidente")
            except Exception as e:
                print(f"    ✗ Falló: {type(e).__name__}: {e}")
        
        # Si hicimos click en el botón, intentar leer el teléfono del CONTENEDOR cercano
        if button_found and 'button' in locals() and button is not None:
            try:
                # Buscar contenedor específico de teléfonos si existe
                phone_container = None
                try:
                    phone_container = driver.execute_script(
                        """
                        var el = arguments[0];
                        var c = el.closest('.phones');
                        if (!c) {
                            // buscar hacia arriba algún ancestro con clase que contenga 'phone'
                            var p = el.parentElement; var d=0;
                            while(p && d<6){
                                if((p.className||'').toLowerCase().includes('phone')){ c=p; break; }
                                p=p.parentElement; d++;
                            }
                        }
                        return c || null;
                        """,
                        button
                    )
                except Exception:
                    phone_container = None

                # 1) Preferir enlaces 'tel:' cercanos al botón (evita capturar WhatsApp genérico)
                tel_info = driver.execute_script(
                    """
                    var el = arguments[0];
                    var container = arguments[1];
                    function isVisible(n){
                        if(!n) return false;
                        var s = window.getComputedStyle(n);
                        return s && s.display !== 'none' && s.visibility !== 'hidden' && n.offsetParent !== null;
                    }
                    function hasWhatsAppAncestor(n){
                        var p = n;
                        while(p){
                            if(p.tagName === 'A'){
                                var h = (p.getAttribute('href')||'').toLowerCase();
                                var c = (p.className||'').toLowerCase();
                                if(h.includes('whatsapp') || h.includes('wa.me') || c.includes('whatsapp') || c.includes('wa')) return true;
                            }
                            p = p.parentElement;
                        }
                        return false;
                    }
                    var container = container || el.closest('section,article,div') || document.body;
                    var links = container.querySelectorAll('a[href^="tel:"]');
                    for(var i=0;i<links.length;i++){
                        var a = links[i];
                        if(isVisible(a) && !hasWhatsAppAncestor(a)){
                            return {href: a.getAttribute('href'), text: a.innerText};
                        }
                    }
                    return null;
                    """,
                    button,
                    phone_container
                )
                if tel_info and (tel_info.get('href') or tel_info.get('text')):
                    href = (tel_info.get('href') or '').strip()
                    txt = (tel_info.get('text') or '').strip()
                    source = href or txt
                    numero = re.sub(r'[^\d+]+', '', source)
                    if numero.startswith('tel:+'):
                        numero = numero[5:]
                    if numero.startswith('tel:'):
                        numero = numero[4:]
                    numero = re.sub(r'[^\d+]', '', numero)
                    if numero:
                        if not numero.startswith('+57'):
                            if numero.startswith('57'):
                                numero = '+' + numero
                            else:
                                numero = '+57' + numero
                        print(f"  ✓ Teléfono leído desde enlace tel:: {numero}")
                        return email, numero

                # Recopilar textos cercanos al botón: el propio, hermanos, padre y ancestros
                candidate_texts = driver.execute_script(
                    """
                    var el = arguments[0];
                    var container = arguments[1];
                    var results = [];
                    function addText(e){ if(e && e.innerText){ results.push(e.innerText); } }
                    if (container) { addText(container); }
                    addText(el);
                    addText(el.nextElementSibling);
                    addText(el.previousElementSibling);
                    addText(el.parentElement);
                    if (el.parentElement){
                        addText(el.parentElement.nextElementSibling);
                        addText(el.parentElement.previousElementSibling);
                    }
                    // Ancestros cercanos (máximo 5 niveles)
                    var p = el.parentElement; var depth = 0;
                    while(p && depth < 5){ addText(p); p = p.parentElement; depth++; }
                    // Si existe un contenedor semántico cercano
                    try {
                        var closest = el.closest('section,article,div');
                        if (closest) addText(closest);
                    } catch(err){}
                    return results;
                    """,
                    button,
                    phone_container
                ) or []

                phone_patterns = [
                    r'\+57[- ]?3[\d\s\-()]{7,10}',
                    r'\+57\s*3[\d\s\-()]{7,10}',
                    r'\+573[\d\s\-()]{8,}',
                    r'\(\+57\)\s*3[\d\s\-()]{7,}',
                    r'3[\d\s\-()]{8,10}',
                    r'3\d{9,10}',
                ]

                # Filtrar textos que parezcan de WhatsApp o CTAs genéricos
                filtered_texts = []
                for text in candidate_texts:
                    if not text:
                        continue
                    low = text.lower()
                    if 'whatsapp' in low or 'wa.me' in low or 'chat' in low:
                        continue
                    filtered_texts.append(text)

                for text in filtered_texts:
                    if not text:
                        continue
                    for pattern in phone_patterns:
                        m = re.search(pattern, text)
                        if m:
                            telefono_raw = m.group(0).strip()
                            telefono_limpio = re.sub(r'[\s\-()]+', '', telefono_raw)
                            if not telefono_limpio.startswith('+57'):
                                if telefono_limpio.startswith('57'):
                                    telefono_limpio = '+' + telefono_limpio
                                else:
                                    telefono_limpio = '+57' + telefono_limpio
                            print(f"  ✓ Teléfono encontrado cerca del botón: {telefono_limpio}")
                            return email, telefono_limpio
            except Exception as e:
                print(f"  Aviso: no fue posible leer teléfono cerca del botón: {type(e).__name__}")

        # Patrones para buscar el teléfono (del más específico al más genérico)
        phone_patterns = [
            r'\+57[- ]?3[\d\s\-()]{7,10}',  # +57 3... (variaciones de formato)
            r'\+57\s*3[\d\s\-()]{7,10}',  # +57 3... con espacios
            r'\+573[\d\s\-()]{8,}',  # +573... con posibles espacios
            r'\(\+57\)\s*3[\d\s\-()]{7,}',  # (+57) 3...
            r'3[\d\s\-()]{8,10}',  # 3xxxxxxxxx (puede estar sin +57)
            r'3\d{9,10}',  # formato simple sin espacios
        ]
        
        # Buscar en el HTML completo (incluye contenido revelado por JavaScript)
        html = driver.page_source
        print(f"  Buscando patrones de teléfono en HTML (longitud: {len(html)} caracteres)...")
        
        # Conjunto para rastrear números únicos y tomar solo el primero
        for i, pattern in enumerate(phone_patterns):
            matches = re.findall(pattern, html)
            if matches:
                print(f"  Patrón {i+1}: encontró {len(matches)} coincidencia(s)")
                # Tomar SOLO el primer número encontrado
                match = matches[0]
                telefono = match.strip()
                # Limpiar espacios, paréntesis y guiones pero mantener +57
                telefono_limpio = re.sub(r'[\s\-()]+', '', telefono)
                # Si no tiene +57 al inicio, agregarlo (es Colombia)
                if not telefono_limpio.startswith('+57'):
                    if telefono_limpio.startswith('57'):
                        telefono_limpio = '+' + telefono_limpio
                    else:
                        telefono_limpio = '+57' + telefono_limpio
                print(f"  ✓ Teléfono encontrado (primer número): {telefono_limpio}")
                return email, telefono_limpio
        
        # Si no encontramos con HTML, buscar en texto visible
        body_text = driver.find_element(By.TAG_NAME, "body").text
        for pattern in phone_patterns:
            phone_match = re.search(pattern, body_text)
            if phone_match:
                telefono = phone_match.group(0).strip()
                telefono = re.sub(r'[\s\-()]+', '', telefono)
                print(f"  ✓ Teléfono encontrado (en texto): {telefono}")
                return email, telefono
        
        if not telefono:
            print(f"  ⚠ Teléfono no encontrado en esta página")
    
    except Exception as e:
        print(f"  Error extrayendo de {url}: {type(e).__name__}: {e}")
    
    return email, telefono
def main():
    parser = argparse.ArgumentParser(description='Extrae emails y teléfonos de perfiles de inmobiliarias')
    parser.add_argument('input', help='Ruta a Excel/CSV con URLs o una URL única')
    parser.add_argument('--column', default='url', help='Nombre de la columna con URLs')
    parser.add_argument('--start-index', type=int, default=1, help='Índice desde el que comenzar (1-based)')
    parser.add_argument('--save-every', type=int, default=50, help='Guardar resultados cada N URLs')
    parser.add_argument('--headless', action='store_true', help='Ejecutar navegador en headless mode')
    parser.add_argument('--max-urls', type=int, default=None, help='Máximo número de URLs a procesar')
    
    args = parser.parse_args()
    
    # Leer URLs
    urls = []
    if args.input.startswith('http'):
        urls = [args.input]
    else:
        try:
            if args.input.lower().endswith('.xlsx') or args.input.lower().endswith('.xls'):
                df = pd.read_excel(args.input)
            else:
                df = pd.read_csv(args.input)
            
            if args.column in df.columns:
                urls = df[args.column].dropna().astype(str).tolist()
            else:
                urls = df.iloc[:, 0].dropna().astype(str).tolist()
        except Exception as e:
            print(f"Error leyendo archivo: {e}")
            return
    
    # Normalizar URLs
    urls = [u if u.startswith('http') else 'https://www.fincaraiz.com.co' + (u if u.startswith('/') else '/' + u) for u in urls]
    
    if args.max_urls:
        urls = urls[:args.max_urls]
    
    # Configurar Selenium - USAR PERFIL CON SESIÓN GUARDADA
    profile_dir = os.path.join(os.path.expanduser("~"), ".fincaraiz_profile")
    
    if not os.path.exists(profile_dir):
        print("=" * 70)
        print("⚠ ERROR: No se encontró el perfil con sesión guardada")
        print("=" * 70)
        print("Necesitas ejecutar primero:")
        print("  python setup_manual_login.py")
        print("\nEsto creará el perfil y guardará tu sesión de login.")
        print("=" * 70)
        return
    
    print(f"Usando perfil con sesión guardada: {profile_dir}")
    
    opts = Options()
    opts.add_argument(f"--user-data-dir={profile_dir}")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_argument("--disable-notifications")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    # Opciones para interactuar mejor con botones
    opts.add_argument("--enable-automation=false")
    opts.add_argument("--disable-popup-blocking")
    
    if args.headless:
        opts.add_argument('--headless=new')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    wait = WebDriverWait(driver, 10)
    
    results = []
    
    try:
        for idx, url in enumerate(urls, 1):
            if idx < args.start_index:
                continue
            
            print(f"[{idx}/{len(urls)}] {url}")
            
            # Manejo de errores robusto con reintentos
            max_retries = 3
            email, phone = None, None
            
            for retry in range(max_retries):
                try:
                    email, phone = extract_contact_info(url, driver, wait)
                    break  # Éxito, salir del bucle de reintentos
                except KeyboardInterrupt:
                    raise  # Permitir Ctrl+C para cancelar
                except Exception as e:
                    if retry < max_retries - 1:
                        print(f"  ⚠ Error (intento {retry+1}/{max_retries}): {type(e).__name__}")
                        print(f"    Reintentando en 1 segundo...")
                        time.sleep(1)
                        # Reiniciar driver si es error de conexión
                        if "ConnectionReset" in str(type(e).__name__) or "InvalidSession" in str(type(e).__name__):
                            try:
                                driver.quit()
                            except:
                                pass
                            driver = webdriver.Chrome(service=service, options=opts)
                            wait = WebDriverWait(driver, 10)
                    else:
                        print(f"  ✗ Error final después de {max_retries} intentos: {type(e).__name__}: {e}")
                        email, phone = None, None
            
            results.append({
                'url': url,
                'email': email or 'No encontrado',
                'telefono': phone or 'No encontrado'
            })
            
            if idx % args.save_every == 0:
                # Guardar parcial
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                partial_file = os.path.join(RESULTS_DIR, f'extraction_emails_partial_{timestamp}.json')
                with open(partial_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"  ✓ Guardado parcial ({len(results)} registros)")
    
    finally:
        driver.quit()
    
    # Guardar resultados finales
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    final_json = os.path.join(RESULTS_DIR, f'extraction_emails_{timestamp}.json')
    final_csv = os.path.join(RESULTS_DIR, f'extraction_emails_{timestamp}.csv')
    
    with open(final_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    df_results = pd.DataFrame(results)
    df_results.to_csv(final_csv, index=False, encoding='utf-8-sig')
    
    print(f"\n✓ Resultados guardados:")
    print(f"  - JSON: {final_json}")
    print(f"  - CSV: {final_csv}")
    print(f"  - Total: {len(results)} registros")

if __name__ == '__main__':
    main()
