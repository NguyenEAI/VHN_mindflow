import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
def search_node(seq):
    for i, node in enumerate(seq):
        if node.get('name') == 'If still has products':
            out.append('Found If still has products')
            if i > 0:
                out.append('Previous node: ' + str(seq[i-1].get('name')))
            out.append('Branches: ' + str(list(node.get('branches', {}).keys())))
            if 'false' in node.get('branches', {}):
                f_branch = node['branches']['false']
                if len(f_branch) > 0:
                    out.append('False branch 1st node: ' + str(f_branch[0].get('name')) + ' properties: ' + str(f_branch[0].get('properties')))
            return True
        if 'sequence' in node:
            if search_node(node['sequence']): return True
        if 'branches' in node:
            for b in node['branches'].values():
                if search_node(b): return True
    return False

search_node(data.get('sequence', []))
with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_if_still.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
