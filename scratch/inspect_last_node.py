import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
def search_node(seq):
    for node in seq:
        if node.get('name') == 'If still has products':
            t_branch = node.get('branches', {}).get('true', [])
            if t_branch:
                out.append('Last node of true branch: ' + str(t_branch[-1].get('name')))
                out.append('Properties: ' + str(t_branch[-1].get('properties')))
            return True
        if 'sequence' in node:
            if search_node(node['sequence']): return True
        if 'branches' in node:
            for b in node['branches'].values():
                if search_node(b): return True
    return False

search_node(data.get('sequence', []))
with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_last_node.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
