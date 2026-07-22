import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def get_node_path(seq, name, path):
    for i, node in enumerate(seq):
        if node.get('name') == name:
            return path + [i]
        if 'sequence' in node:
            r = get_node_path(node['sequence'], name, path + [i, 'sequence'])
            if r: return r
        if 'branches' in node:
            for b_name, b_seq in node['branches'].items():
                r = get_node_path(b_seq, name, path + [i, 'branches', b_name])
                if r: return r
    return None

path = get_node_path(data.get('sequence', []), 'Sheet Product', [])
with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\path_sheet_product.txt', 'w', encoding='utf-8') as f:
    f.write(str(path))
