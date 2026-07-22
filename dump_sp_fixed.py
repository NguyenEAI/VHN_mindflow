import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def get_node(seq, name, type_str):
    for node in seq:
        if node.get('name') == name and node.get('type') == type_str:
            return node
        if 'sequence' in node:
            res = get_node(node['sequence'], name, type_str)
            if res: return res
        if 'branches' in node:
            for b in node['branches'].values():
                res = get_node(b, name, type_str)
                if res: return res
    return None

sheet_product = get_node(data.get('sequence', []), 'Sheet Product', 'block')
with open('sheet_product_check.txt', 'w', encoding='utf-8') as f:
    if sheet_product:
        f.write(json.dumps(sheet_product, indent=2, ensure_ascii=False))
    else:
        f.write('Sheet Product not found')
