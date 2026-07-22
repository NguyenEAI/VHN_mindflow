import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
def print_tree(node, depth=0):
    indent = '  ' * depth
    out.append(f'{indent}{node.get("name")} ({node.get("type")})')
    if 'sequence' in node:
        for n in node['sequence']:
            print_tree(n, depth + 1)
    if 'branches' in node:
        for b_name, b_seq in node['branches'].items():
            out.append(f'{indent}  Branch: {b_name}')
            for n in b_seq:
                print_tree(n, depth + 2)

node_5 = data['sequence'][5]['branches']['order'][5]
print_tree(node_5)

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_order_exit.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
