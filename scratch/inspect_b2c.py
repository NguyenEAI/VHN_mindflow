import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
b2c = data['sequence'][5]['branches']['b2c_consult']
for i, node in enumerate(b2c):
    out.append(f'Node {i}: {node.get("name")}')

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_b2c.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
