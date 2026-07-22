import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

node = data['sequence'][5]['branches']['b2c_consult'][3]['branches']['true'][0]
out = ['Name: ' + node.get('name'), 'Type: ' + node.get('type')]
with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_original_node.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
