import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

node = data['sequence'][5]['branches']['b2c_consult'][3]

out = []
out.append('Name: ' + str(node.get('name')))
out.append('Type: ' + str(node.get('type')))
out.append('Properties: ' + str(node.get('properties')))
if 'branches' in node:
    out.append('Branches: ' + str(list(node['branches'].keys())))
    if 'false' in node['branches']:
        out.append('False branch length: ' + str(len(node['branches']['false'])))
        for child in node['branches']['false']:
            out.append('  False child: ' + str(child.get('name')))

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_node3.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
