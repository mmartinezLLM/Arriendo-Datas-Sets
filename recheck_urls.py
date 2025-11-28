import os
import re
import json
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait

# Reusar la lógica de extracción ya probada
from extract_emails_fast import extract_contact_info

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "resultados")
RECHECK_LIST = os.path.join(RESULTS_DIR, "recheck_urls.txt")
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
OUT_JSON = os.path.join(RESULTS_DIR, f"extraction_emails_RECHECK_{TS}.json")
OUT_CSV = os.path.join(RESULTS_DIR, f"extraction_emails_RECHECK_{TS}.csv")
PROFILE_DIR = os.path.join(os.path.expanduser("~"), ".fincaraiz_profile")

PHONE_NOT_FOUND = "No encontrado"


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={PROFILE_DIR}")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    return driver


def run_recheck():
    if not os.path.exists(RECHECK_LIST):
        raise FileNotFoundError(f"No existe {RECHECK_LIST}")
    with open(RECHECK_LIST, "r", encoding="utf-8") as f:
        urls = [l.strip() for l in f if l.strip()]

    print(f"Total URLs a revalidar: {len(urls)}")
    os.makedirs(RESULTS_DIR, exist_ok=True)

    driver = create_driver()
    wait = WebDriverWait(driver, 20)

    results = []
    try:
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] {url}")
            attempt = 0
            email = ""
            phone = PHONE_NOT_FOUND
            while attempt < 3:
                attempt += 1
                try:
                    e, p = extract_contact_info(url, driver, wait)
                    email = e or ""
                    phone = p or PHONE_NOT_FOUND
                    break
                except KeyboardInterrupt:
                    raise
                except Exception as ex:
                    print(f"  Intento {attempt}: error {type(ex).__name__}: {ex}")
                    # Reiniciar driver en errores de sesión
                    try:
                        driver.quit()
                    except Exception:
                        pass
                    time.sleep(2)
                    driver = create_driver()
                    wait = WebDriverWait(driver, 20)
            results.append({"url": url, "email": email, "telefono": phone})

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    # Guardar resultados
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    try:
        # CSV simple
        import pandas as pd
        pd.DataFrame(results).to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    except Exception as e:
        print("Advertencia al escribir CSV:", e)

    print("Listo RECHECK.")
    print("  ", OUT_JSON)
    print("  ", OUT_CSV)


if __name__ == "__main__":
    print("Usando perfil con sesión guardada:", PROFILE_DIR)
    run_recheck()
