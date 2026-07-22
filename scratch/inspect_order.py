import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
order_branch = data['sequence'][5]['branches']['order']
for i, node in enumerate(order_branch):
    out.append(f'Node {i}: {node.get("name")} ({node.get("type")})')

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_order.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
