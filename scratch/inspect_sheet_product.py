import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
seq = data['sequence'][5]['branches']['b2c_consult'][3]['branches']['true'][0]['sequence']
for i, node in enumerate(seq):
    out.append(f'Node {i}: {node.get("name")}')

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_sheet_product.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
