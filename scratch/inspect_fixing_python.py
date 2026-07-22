import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
node = data['sequence'][12]['sequence'][0]['branches']['true'][0]['sequence'][1]
out.append('Node name: ' + str(node.get('name')))
out.append('Node type: ' + str(node.get('type')))
out.append('code: ' + repr(node.get('properties', {}).get('code')))

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_fixing_python.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
