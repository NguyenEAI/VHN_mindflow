import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
node = data['sequence'][5]['branches']['order'][5]
out.append('Node name: ' + str(node.get('name')))
f_branch = node.get('branches', {}).get('false', [])
for i, n in enumerate(f_branch):
    out.append(f'False branch {i}: {n.get("name")} ({n.get("type")})')

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_exit_false.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
