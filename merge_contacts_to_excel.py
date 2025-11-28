"""
Fusiona los archivos de contactos (emails / teléfonos) con el Excel final de extracción.
- Lee `resultados/extraction_completo_fusionado.xlsx` si existe (preferido), si no lee `inmo FR 1.xlsx`.
- Lee todos los JSON en `resultados/` que parezcan contener emails/contact_info.
- Empareja por ID numérico presente en la URL (ej: .../176359705) y añade columnas `email` y `telefono`.
- Guarda un nuevo Excel `resultados/extraction_completo_with_contacts.xlsx` y CSV/JSON equivalentes.

Uso:
python merge_contacts_to_excel.py

"""
import os
import re
import json
from glob import glob
from collections import defaultdict

try:
    import pandas as pd
except Exception as e:
    raise SystemExit('Pandas es requerido para este script. Instálalo y vuelve a intentar.')

ROOT = os.path.dirname(__file__)
RESULTS = os.path.join(ROOT, 'resultados')
MASTER_XLSX = os.path.join(RESULTS, 'extraction_completo_fusionado.xlsx')
FALLBACK_INPUT = os.path.join(os.path.dirname(ROOT), 'inmo FR 1.xlsx')
OUT_XLSX = os.path.join(RESULTS, 'extraction_completo_with_contacts.xlsx')
OUT_CSV = os.path.join(RESULTS, 'extraction_completo_with_contacts.csv')
OUT_JSON = os.path.join(RESULTS, 'extraction_completo_with_contacts.json')

EMAIL_KEYS = {'email', 'correo', 'e-mail'}
PHONE_KEYS = {'telefono', 'teléfono', 'phone', 'telefono_formatted', 'telefono_visible', 'telefono_mostrar'}

ID_RE = re.compile(r'/?(?:perfil/)?(\d+)(?:/)?$')
GENERIC_ID_RE = re.compile(r'(\d{5,})')


def extract_id_from_url(url):
    if not isinstance(url, str):
        return None
    m = ID_RE.search(url)
    if m:
        return m.group(1)
    m2 = GENERIC_ID_RE.search(url)
    if m2:
        return m2.group(1)
    return None


def load_contact_json_files(resultados_dir):
    mapping = defaultdict(lambda: {'emails': set(), 'phones': set(), 'sources': set()})
    patterns = [
        os.path.join(resultados_dir, 'contact_info_*.json'),
        os.path.join(resultados_dir, 'extraction_emails*.json'),
        os.path.join(resultados_dir, 'extraction_emails_partial_*.json'),
        os.path.join(resultados_dir, 'extraction_emails_partial_latest.json'),
    ]
    files = []
    for pat in patterns:
        files.extend(glob(pat))
    # Also include any json that contains 'contact' or 'email' in its filename
    extra = [p for p in glob(os.path.join(resultados_dir, '*.json')) if ('contact' in os.path.basename(p).lower() or 'email' in os.path.basename(p).lower())]
    for p in extra:
        if p not in files:
            files.append(p)

    files = sorted(set(files))
    print(f'Leyendo {len(files)} archivos JSON de contactos...')

    for p in files:
        try:
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f'  ⚠️ No se pudo leer {p}: {e}')
            continue
        if not isinstance(data, list):
            continue
        for entry in data:
            url = entry.get('url') or entry.get('link') or entry.get('href')
            if not url:
                # sometimes entries contain 'perfil' or id only
                continue
            idv = extract_id_from_url(url)
            if not idv:
                # try to find any numeric id in url
                m = GENERIC_ID_RE.search(url)
                if m:
                    idv = m.group(1)
            if not idv:
                continue
            # find email and phone
            email = None
            phone = None
            for k, v in entry.items():
                key = k.lower().strip()
                if key in EMAIL_KEYS and v:
                    email = v
                if key in PHONE_KEYS and v:
                    phone = v
                # also accept fields literally named 'email' or containing '@'
                if (not email) and isinstance(v, str) and ('@' in v):
                    email = v
                if (not phone) and isinstance(v, str) and re.search(r'\+?\d[\d\s\-()]{6,}', v):
                    phone = v
            if email:
                mapping[idv]['emails'].add(email.strip())
            if phone:
                mapping[idv]['phones'].add(phone.strip())
            mapping[idv]['sources'].add(os.path.basename(p))
    return mapping


def main():
    # Load master dataframe
    if os.path.exists(MASTER_XLSX):
        print(f'Leyendo master desde {MASTER_XLSX}')
        df = pd.read_excel(MASTER_XLSX)
    elif os.path.exists(FALLBACK_INPUT):
        print(f'Leyendo master desde {FALLBACK_INPUT} (fallback)')
        df = pd.read_excel(FALLBACK_INPUT)
        # ensure column name 'url' exists
        if 'url' not in df.columns:
            df.rename(columns={df.columns[0]: 'url'}, inplace=True)
    else:
        raise SystemExit('No se encontró archivo maestro (extraction_completo_fusionado.xlsx ni inmo FR 1.xlsx)')

    # Normalize url column name
    if 'url' not in df.columns:
        possible = [c for c in df.columns if 'url' in c.lower() or 'link' in c.lower() or 'href' in c.lower()]
        if possible:
            df.rename(columns={possible[0]: 'url'}, inplace=True)
        else:
            df['url'] = df.iloc[:, 0].astype(str)

    # Load existing contact JSONs
    mapping = load_contact_json_files(RESULTS)
    print(f'Contactos únicos encontrados para {len(mapping)} ids')

    # Prepare columns
    df['id_perfil'] = df['url'].astype(str).apply(extract_id_from_url)
    df['email'] = ''
    df['telefono'] = ''
    df['contact_sources'] = ''

    found_email = 0
    found_phone = 0

    for i, row in df.iterrows():
        idv = row['id_perfil']
        if not idv:
            # try to extract from URL by generic pattern
            idv = GENERIC_ID_RE.search(str(row['url']))
            idv = idv.group(1) if idv else None
        if not idv:
            continue
        data = mapping.get(idv)
        if not data:
            continue
        emails = sorted(x for x in data['emails'] if x)
        phones = sorted(x for x in data['phones'] if x)
        if emails:
            df.at[i, 'email'] = '; '.join(emails)
            found_email += 1
        if phones:
            df.at[i, 'telefono'] = '; '.join(phones)
            found_phone += 1
        if data['sources']:
            df.at[i, 'contact_sources'] = '; '.join(sorted(list(data['sources'])))

    print(f'Filas con email encontrado: {found_email} / {len(df)}')
    print(f'Filas con telefono encontrado: {found_phone} / {len(df)}')

    # Save outputs
    df_out = df.drop(columns=['id_perfil'])
    try:
        df_out.to_excel(OUT_XLSX, index=False)
        print(f'✓ Archivo Excel guardado en: {OUT_XLSX}')
    except Exception as e:
        print('Error guardando Excel:', e)
    try:
        df_out.to_csv(OUT_CSV, index=False, encoding='utf-8-sig')
        print(f'✓ Archivo CSV guardado en: {OUT_CSV}')
    except Exception as e:
        print('Error guardando CSV:', e)
    try:
        df_out.to_json(OUT_JSON, orient='records', force_ascii=False, indent=2)
        print(f'✓ Archivo JSON guardado en: {OUT_JSON}')
    except Exception as e:
        print('Error guardando JSON:', e)


if __name__ == '__main__':
    main()
