import os
import re
import json
from glob import glob
import pandas as pd
from datetime import datetime

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
    v = phone_separators.sub("", v)
    if v.startswith("00"):
        v = "+" + v[2:]
    if re.fullmatch(r"3\d{9}", v):
        v = "+57" + v
    return v


def valid_phone(value: str) -> bool:
    if not value or value.strip().lower() == PHONE_NOT_FOUND.lower():
        return False
    v = normalize_phone(value)
    if re.fullmatch(r"\+57\d{10}", v):
        return True
    if re.fullmatch(r"3\d{9}", v):
        return True
    digits = re.sub(r"\D", "", v)
    if v.startswith("+57") and len(digits) >= 12:
        return True
    return False


def load_all_results_with_overrides() -> list:
    pattern = os.path.join(RESULTS_DIR, "extraction_emails_*.json")
    files = sorted(glob(pattern), key=os.path.getmtime)
    if not files:
        raise FileNotFoundError(f"No se encontraron archivos en {RESULTS_DIR} con patrón extraction_emails_*.json")

    records_by_url = {}
    source_by_url = {}

    # RECHECK debe sobrescribir cualquier anterior aunque ambos sean "válidos"
    def is_override(path: str) -> bool:
        name = os.path.basename(path).upper()
        return "RECHECK" in name or "OVERRIDE" in name

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
            if not url:
                continue
            rec_out = {"url": url, "email": email, "telefono": normalize_phone(phone) if phone else PHONE_NOT_FOUND}

            if url not in records_by_url:
                records_by_url[url] = rec_out
                source_by_url[url] = path
            else:
                existing = records_by_url[url]
                if is_override(path):
                    records_by_url[url] = rec_out
                    source_by_url[url] = path
                else:
                    # Si no es override, preferir válidos sobre no válidos
                    if not valid_phone(existing.get("telefono")) and valid_phone(rec_out.get("telefono")):
                        records_by_url[url] = rec_out
                        source_by_url[url] = path
                    # si ambos válidos, mantener el que ya estaba (no override)

    return list(records_by_url.values())


def order_by_input_excel(records: list, input_excel_path: str) -> (pd.DataFrame, str):
    try:
        df_input = pd.read_excel(input_excel_path)
        url_col = None
        for c in df_input.columns:
            if str(c).strip().lower() in ("url", "links", "enlace", "link"):
                url_col = c
                break
        if url_col is None:
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
        return df, str(url_col)
    except Exception:
        return pd.DataFrame(records), "url"


def main():
    print("Buscando resultados (con overrides) en:", RESULTS_DIR)
    all_records = load_all_results_with_overrides()
    print(f"Registros únicos por URL: {len(all_records)}")

    df, url_col_name = order_by_input_excel(all_records, INPUT_EXCEL_DEFAULT)

    for col in ("url", "email", "telefono"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    df["telefono"] = df["telefono"].apply(normalize_phone)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    final_records = df.to_dict(orient="records")
    with open(FINAL_JSON, "w", encoding="utf-8") as f:
        json.dump(final_records, f, ensure_ascii=False, indent=2)
    df.to_csv(FINAL_CSV, index=False, encoding="utf-8-sig")

    # Hoja Con_Origen con todas las columnas del Excel original + email/telefono
    df_with_origin = None
    try:
        df_input = pd.read_excel(INPUT_EXCEL_DEFAULT)
        if url_col_name not in df_input.columns:
            # Re detectar
            for c in df_input.columns:
                if str(c).strip().lower() in ("url", "links", "enlace", "link"):
                    url_col_name = c
                    break
            if url_col_name not in df_input.columns:
                url_col_name = df_input.columns[0]
        res_map = {r["url"]: {"email": r.get("email", ""), "telefono": r.get("telefono", PHONE_NOT_FOUND)} for r in final_records}
        df_with_origin = df_input.copy()
        df_with_origin["email"] = df_with_origin[url_col_name].astype(str).str.strip().map(lambda u: res_map.get(u, {}).get("email", ""))
        df_with_origin["telefono"] = df_with_origin[url_col_name].astype(str).str.strip().map(lambda u: res_map.get(u, {}).get("telefono", PHONE_NOT_FOUND))
        df_with_origin["telefono"] = df_with_origin["telefono"].apply(normalize_phone)
    except Exception as e:
        print("Advertencia al preparar hoja Con_Origen:", e)

    try:
        with pd.ExcelWriter(FINAL_XLSX) as writer:
            df.to_excel(writer, sheet_name="Resultados", index=False)
            if df_with_origin is not None:
                df_with_origin.to_excel(writer, sheet_name="Con_Origen", index=False)
    except Exception as e:
        print("Advertencia al escribir Excel:", e)

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
