import os
import re
import json
from datetime import datetime
from glob import glob

import pandas as pd

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "resultados")
INPUT_EXCEL_DEFAULT = os.path.join(os.path.dirname(__file__), "..", "inmo FR 1.xlsx")
FINAL_JSON = os.path.join(RESULTS_DIR, "extraction_emails_FINAL.json")
FINAL_CSV = os.path.join(RESULTS_DIR, "extraction_emails_FINAL.csv")
FINAL_XLSX = os.path.join(RESULTS_DIR, "extraction_emails_FINAL.xlsx")

PHONE_NOT_FOUND = "No encontrado"

phone_separators = re.compile(r"[\s\-()]")


def normalize_phone(value: str) -> str:
    if not value or value.strip().lower() == PHONE_NOT_FOUND.lower():
        return PHONE_NOT_FOUND
    v = value.strip()
    # Remove common separators
    v = phone_separators.sub("", v)
    # Ensure leading + only once
    if v.startswith("00"):  # 0057...
        v = "+" + v[2:]
    # If it is a 10-digit mobile starting with 3, add +57
    if re.fullmatch(r"3\d{9}", v):
        v = "+57" + v
    # Keep other formats as-is if they already include country code
    return v


def valid_phone(value: str) -> bool:
    if not value or value.strip().lower() == PHONE_NOT_FOUND.lower():
        return False
    v = normalize_phone(value)
    # Consider valid if it looks like +57 followed by 10 digits, or starts with 3 and 10 digits
    if re.fullmatch(r"\+57\d{10}", v):
        return True
    if re.fullmatch(r"3\d{9}", v):
        return True
    # Some entries may be already +57XXXXXXXXXX with separators removed
    # If it contains at least 10 digits and includes +57, accept
    digits = re.sub(r"\D", "", v)
    if v.startswith("+57") and len(digits) >= 12:
        return True
    return False


def load_all_results() -> list:
    pattern = os.path.join(RESULTS_DIR, "extraction_emails_*.json")
    files = sorted(glob(pattern), key=os.path.getmtime)
    if not files:
        raise FileNotFoundError(f"No se encontraron archivos en {RESULTS_DIR} con patrón extraction_emails_*.json")

    records_by_url = {}
    chosen_file_by_url = {}

    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        for rec in data:
            url = (rec.get("url") or rec.get("URL") or "").strip()
            email = (rec.get("email") or rec.get("correo") or "").strip()
            phone = (rec.get("telefono") or rec.get("tel") or rec.get("phone") or "").strip()

            # Normalize phone once for decision making, but keep original fields
            phone_norm = normalize_phone(phone)
            rec_out = {"url": url, "email": email, "telefono": phone_norm if phone_norm else PHONE_NOT_FOUND}

            if not url:
                continue

            if url not in records_by_url:
                records_by_url[url] = rec_out
                chosen_file_by_url[url] = path
            else:
                existing = records_by_url[url]
                # Prefer a record with a valid phone over one without
                if not valid_phone(existing.get("telefono")) and valid_phone(rec_out.get("telefono")):
                    records_by_url[url] = rec_out
                    chosen_file_by_url[url] = path
                # If both have valid or both invalid, keep the existing (earlier) one
                # to preserve first successful capture and avoid oscillation.

    # Return as list
    merged = list(records_by_url.values())
    return merged


def order_by_input_excel(records: list, input_excel_path: str) -> pd.DataFrame:
    try:
        df_input = pd.read_excel(input_excel_path)
        # Try common column names
        url_col = None
        for c in df_input.columns:
            if str(c).strip().lower() in ("url", "links", "enlace", "link"):
                url_col = c
                break
        if url_col is None:
            # Fallback: first column
            url_col = df_input.columns[0]
        order_urls = [str(u).strip() for u in df_input[url_col].tolist()]
        rec_map = {r.get("url", ""): r for r in records}
        ordered = []
        for u in order_urls:
            r = rec_map.get(u)
            if r is None:
                ordered.append({"url": u, "email": "", "telefono": PHONE_NOT_FOUND})
            else:
                ordered.append(r)
        df = pd.DataFrame(ordered)
        return df
    except Exception:
        # If input excel not found or unreadable, just return dataframe from records
        return pd.DataFrame(records)


def main():
    print("Buscando resultados en:", RESULTS_DIR)
    all_records = load_all_results()
    print(f"Registros únicos por URL encontrados: {len(all_records)}")

    # Deduplicate exact url/email/telefono rows if any
    df = order_by_input_excel(all_records, INPUT_EXCEL_DEFAULT)

    # Basic cleanup: strip spaces
    for col in ("url", "email", "telefono"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Sanity: ensure telefono normalized consistently
    df["telefono"] = df["telefono"].apply(normalize_phone)

    # Save outputs
    os.makedirs(RESULTS_DIR, exist_ok=True)
    final_records = df.to_dict(orient="records")
    with open(FINAL_JSON, "w", encoding="utf-8") as f:
        json.dump(final_records, f, ensure_ascii=False, indent=2)
    df.to_csv(FINAL_CSV, index=False, encoding="utf-8-sig")
    try:
        df.to_excel(FINAL_XLSX, index=False)
    except Exception as e:
        print("Advertencia al escribir Excel:", e)

    # Stats
    total = len(df)
    con_tel = int((df["telefono"].str.lower() != PHONE_NOT_FOUND.lower()).sum()) if "telefono" in df.columns else 0
    sin_tel = total - con_tel
    print("Listo.")
    print("Salida:")
    print("  ", FINAL_JSON)
    print("  ", FINAL_CSV)
    print("  ", FINAL_XLSX)
    print(f"Totales: {total} | Con teléfono: {con_tel} | Sin teléfono: {sin_tel}")


if __name__ == "__main__":
    main()
