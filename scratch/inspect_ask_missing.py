import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
node = data['sequence'][5]['branches']['order'][5]['branches']['false'][0]['branches']['true'][0]['branches']['true'][0]
out.append('Node name: ' + str(node.get('name')))
out.append('Node text: ' + repr(node.get('properties', {}).get('text')))

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_ask_missing.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
