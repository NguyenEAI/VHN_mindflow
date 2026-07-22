import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
for i in [1, 4, 8]:
    node = data['sequence'][5]['branches']['b2c_consult'][i]
    out.append(f'Node {i}: {node.get("name")}')
    instruction = node.get('properties', {}).get('instruction', '')
    if 'session.extra.product_information' in instruction:
        out.append('  Found session.extra.product_information in instruction!')
    else:
        out.append('  Not found in instruction.')

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_prompts.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
