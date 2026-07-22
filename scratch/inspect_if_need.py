import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
b2c = data['sequence'][5]['branches']['b2c_consult']
for i, node in enumerate(b2c):
    if node.get('name') == 'If need product info':
        out.append('Found If need product info')
        out.append(str(node['properties']['condition']))
        
        if 'false' in node.get('branches', {}):
            out.append('False branch:')
            for n in node['branches']['false']:
                out.append(f'  {n.get("name")}')
        else:
            out.append('No false branch!')

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_if_need.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
