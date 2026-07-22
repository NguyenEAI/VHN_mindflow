import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
node = data['sequence'][5]['branches']['b2c_consult'][3]['branches']['true'][0]['sequence'][2]['branches']['true'][0]
out.append('Node name: ' + str(node.get('name')))
out.append('Node type: ' + str(node.get('type')))
out.append('varValue: ' + repr(node.get('properties', {}).get('varValue')))

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_bad_node.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
