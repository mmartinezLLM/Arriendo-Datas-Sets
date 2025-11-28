#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugear y analizar la estructura del JSON __NEXT_DATA__
"""
import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def analizar_url(url):
    """Analiza una URL y muestra la estructura del JSON"""
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print(f"\n{'='*80}")
        print(f"Analizando: {url}")
        print(f"{'='*80}\n")
        
        driver.get(url)
        time.sleep(3)
        
        html = driver.page_source
        
        # Buscar __NEXT_DATA__
        match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.+?)</script>', html, re.DOTALL)
        if not match:
            print("❌ No se encontró __NEXT_DATA__")
            return
        
        json_data = json.loads(match.group(1))
        props = json_data.get('props', {}).get('pageProps', {})
        data = props.get('data', {})
        technical_sheet = props.get('technicalSheet', [])
        
        # Guardar JSON completo para análisis
        timestamp = str(int(time.time()))
        filename = f"debug_json_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({'data': data, 'technical_sheet': technical_sheet}, f, ensure_ascii=False, indent=2)
        
        print(f"📄 JSON guardado en: {filename}\n")
        
        # Mostrar campos importantes
        print("CAMPOS PRINCIPALES:")
        print(f"  ID: {data.get('id')}")
        print(f"  Legacy ID: {data.get('legacyId')}")
        print(f"  Title: {data.get('title')}")
        print(f"  Business Type: {data.get('businessType')}")
        print(f"  Property Type: {data.get('propertyType')}")
        print(f"  Status: {data.get('status')}")
        
        print(f"\n  Client: {data.get('client')}")
        print(f"  Price: {data.get('price')}")
        print(f"  Locations: {data.get('locations')}")
        
        print(f"\n  Gallery (primeras 3): {data.get('gallery', [])[:3]}")
        print(f"  Facilities (primeras 5): {data.get('facilities', [])[:5]}")
        
        print(f"\nTECHNICAL SHEET ({len(technical_sheet)} items):")
        for item in technical_sheet[:15]:
            print(f"  {item.get('field')}: {item.get('value')}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    urls = [
        "https://www.fincaraiz.com.co/casa-en-venta-en-pance-cali/191887750",
        "https://www.fincaraiz.com.co/local-en-arriendo-en-guayaquil-cali/192758986",
        "https://www.fincaraiz.com.co/casa-en-venta-en-juan-de-ampudia-jamundi/191879923",
        "https://www.fincaraiz.com.co/oficina-en-venta-en-san-pedro-cali/191902628",
        "https://www.fincaraiz.com.co/apartamento-en-venta-en-versalles-cali/193006583",
    ]
    
    for url in urls:
        analizar_url(url)
        time.sleep(2)
