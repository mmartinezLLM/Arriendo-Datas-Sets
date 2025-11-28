"""
Inspecciona la estructura real de fincaraiz.com.co/inmobiliarias
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json

print("Abriendo fincaraiz.com.co/inmobiliarias...")
options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get('https://www.fincaraiz.com.co/inmobiliarias')
time.sleep(6)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

print("\n=== ANÁLISIS DE ESTRUCTURA ===\n")

# Guardar HTML completo
with open('resultados/html_completo.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ HTML completo guardado")

# Buscar todas las clases únicas
todas_clases = set()
for elem in soup.find_all():
    clases = elem.get('class', [])
    if clases:
        todas_clases.update(clases)

print(f"\nClases encontradas ({len(todas_clases)}):")
clases_relevantes = [c for c in todas_clases if any(kw in c.lower() for kw in ['company', 'card', 'inmobiliaria', 'item', 'item-', 'grid', 'content'])]
for clase in sorted(clases_relevantes)[:20]:
    print(f"  - {clase}")

# Buscar todos los data-testid
data_testids = {}
for elem in soup.find_all(attrs={'data-testid': True}):
    testid = elem.get('data-testid')
    if testid not in data_testids:
        data_testids[testid] = 0
    data_testids[testid] += 1

print(f"\ndata-testid encontrados:")
for testid, count in sorted(data_testids.items())[:15]:
    print(f"  - {testid}: {count} elementos")

# Buscar estructuras con imágenes + texto
print("\nBuscando cards con imágenes...")
cards_con_img = soup.find_all(lambda tag: tag.name and tag.find('img') and tag.find(['h2', 'h3', 'h4', 'span']))
print(f"Cards con imagen encontradas: {len(cards_con_img)}")

if cards_con_img:
    print("\nPrimer card encontrado:")
    primer_card = cards_con_img[0]
    print(f"Tag: {primer_card.name}")
    print(f"Clases: {primer_card.get('class')}")
    print(f"ID: {primer_card.get('id')}")
    
    # Buscar títulos dentro
    titulos = primer_card.find_all(['h2', 'h3', 'h4', 'span'])
    if titulos:
        print(f"Títulos encontrados: {[t.get_text(strip=True)[:50] for t in titulos[:3]]}")
    
    # Buscar enlaces
    enlaces = primer_card.find_all('a', href=True)
    if enlaces:
        print(f"Enlaces: {[e.get('href')[:50] for e in enlaces[:3]]}")

# Buscar botones
botones = soup.find_all('button', limit=10)
print(f"\nBotones encontrados: {len(soup.find_all('button'))}")
for btn in botones[:5]:
    txt = btn.get_text(strip=True)
    if txt:
        print(f"  - {txt[:40]}")

# Buscar inputs
inputs = soup.find_all('input', limit=10)
print(f"\nInputs encontrados: {len(soup.find_all('input'))}")
for inp in inputs[:5]:
    placeholder = inp.get('placeholder', '')
    tipo = inp.get('type', '')
    if placeholder:
        print(f"  - [{tipo}] {placeholder}")

driver.quit()
print("\n✓ Inspección completada. Verifica resultados/html_completo.html")
