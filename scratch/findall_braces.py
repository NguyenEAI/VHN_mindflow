import json, re

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    text = f.read()

matches = re.findall(r'\{\{.*?\}\}', text)
out = []
for m in matches:
    if not m.startswith('{{ session.extra') and not m.startswith('{{ bot_uuid') and not m.startswith('{{ channel') and not m.startswith('{{ thread') and not m.startswith('{{ user_msg') and not m.startswith('{{ company_'):
        out.append(m)

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\findall_braces.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
