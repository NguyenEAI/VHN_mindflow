import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

node5 = data['sequence'][5]
out = []
out.append('Node 5 name: ' + str(node5.get('name')))
out.append('Node 5 type: ' + str(node5.get('type')))
out.append('Node 5 componentType: ' + str(node5.get('componentType')))
if 'branches' in node5:
    out.append('Node 5 branches: ' + str(list(node5.get('branches').keys())))

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\main_switch.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
