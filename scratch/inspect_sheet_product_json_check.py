import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
node = data['sequence'][5]['branches']['b2c_consult'][3]['branches']['true'][0]['sequence'][2]
out.append('Branches in If json_check: ' + str(node.get('branches', {}).keys()))
out.append('True branch nodes:')
if 'true' in node.get('branches', {}):
    for i, n in enumerate(node['branches']['true']):
        out.append(f'  Node {i}: {n.get("name")}')

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_sheet_product_json_check.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
