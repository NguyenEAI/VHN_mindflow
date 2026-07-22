import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
node = data['sequence'][5]['branches']['b2c_consult'][3]['branches']['true'][0]['sequence'][4]['branches']['true'][4]
out.append('Node name: ' + str(node.get('name')))
out.append('Node type: ' + str(node.get('type')))
out.append('expression: ' + repr(node.get('properties', {}).get('expression', '')))

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_format_info.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
