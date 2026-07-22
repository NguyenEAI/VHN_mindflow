import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
def find_parent_seq(seq):
    for i, node in enumerate(seq):
        if node.get('name') == 'Set topic':
            out.append('Found Set topic in sequence!')
            if i > 0:
                prev = seq[i-1]
                out.append('Previous node is: ' + str(prev.get('name')) + ' type: ' + str(prev.get('type')))
                out.append('Properties: ' + str(prev.get('properties')))
            return True
        if 'sequence' in node:
            if find_parent_seq(node['sequence']): return True
        if 'branches' in node:
            for b in node['branches'].values():
                if find_parent_seq(b): return True
    return False

find_parent_seq(data.get('sequence', []))
with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\find_prev_node.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
