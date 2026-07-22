import json

with open('VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
nodes = []
def find_node(seq):
    for node in seq:
        if node.get('name') == 'Format Product Info':
            nodes.append(node)
        if 'sequence' in node:
            find_node(node['sequence'])
        if 'branches' in node:
            for b in node['branches'].values():
                find_node(b)
find_node(data.get('sequence', []))
with open('format_product_info_dump.py', 'w', encoding='utf-8') as f:
    f.write(nodes[0].get('properties', {}).get('expression', ''))
