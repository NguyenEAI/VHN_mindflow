import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
def search_node(seq, path=[]):
    for i, node in enumerate(seq):
        if node.get('name') == 'Sheet Product':
            out.append('Found at path in VHN_fixing.json: ' + str(path + [i]))
            return True
        if 'sequence' in node:
            if search_node(node['sequence'], path + [i, 'sequence']): return True
        if 'branches' in node:
            for b_name, b_seq in node['branches'].items():
                if search_node(b_seq, path + [i, 'branches', b_name]): return True
    return False

search_node(data.get('sequence', []))
with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_fixing_sheet.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
