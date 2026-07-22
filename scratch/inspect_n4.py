import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
n4 = data['sequence'][4]
out = []
out.append('Node 4: ' + str(n4.get('name')) + ' Type: ' + str(n4.get('type')))
out.append('Properties: ' + str(n4.get('properties')))

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_n4.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
