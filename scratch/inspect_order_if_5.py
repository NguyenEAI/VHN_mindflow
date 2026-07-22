import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
n = data['sequence'][5]['branches']['order'][5]
out.append('Name: ' + str(n.get('name')))
out.append('Type: ' + str(n.get('type')))
out.append('Properties: ' + str(n.get('properties')))

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_order_if_5.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
