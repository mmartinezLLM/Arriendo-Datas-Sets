# Leer archivo
with open('property_crawler_selenium.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar inicio y fin de urls_prueba
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if 'urls_prueba = [' in line:
        start_idx = i
    if start_idx is not None and line.strip() == ']':
        end_idx = i
        break

# Extraer URLs
urls = []
for i in range(start_idx + 1, end_idx):
    line = lines[i].strip()
    if line and line.startswith('http'):
        urls.append(line)

print(f"Encontradas {len(urls)} URLs")

# Crear nuevas líneas con formato correcto
new_lines = ['    urls_prueba = [\n']
for url in urls:
    new_lines.append(f'        "{url}",\n')
new_lines[-1] = new_lines[-1].rstrip(',\n') + '\n'  # Quitar última coma
new_lines.append('    ]\n')

# Reconstruir archivo
new_content = lines[:start_idx] + new_lines + lines[end_idx + 1:]

# Guardar
with open('property_crawler_selenium.py', 'w', encoding='utf-8') as f:
    f.writelines(new_content)

print(f'✅ Arregladas {len(urls)} URLs con comillas y comas')
