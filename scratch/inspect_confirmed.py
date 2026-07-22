import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
node = data['sequence'][5]['branches']['order'][5]['branches']['false'][0]
out.append('Node name: ' + str(node.get('name')))
out.append('Branches: ' + str(list(node.get('branches', {}).keys())))
t_branch = node.get('branches', {}).get('true', [])
f_branch = node.get('branches', {}).get('false', [])

out.append('True branch length: ' + str(len(t_branch)))
if t_branch:
    out.append('  Last node of true branch: ' + str(t_branch[-1].get('name')))
    out.append('  Type: ' + str(t_branch[-1].get('type')))
out.append('False branch length: ' + str(len(f_branch)))
if f_branch:
    out.append('  First node of false branch: ' + str(f_branch[0].get('name')))
    out.append('  Type: ' + str(f_branch[0].get('type')))

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_confirmed.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
