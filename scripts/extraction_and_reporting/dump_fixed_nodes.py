import json
import traceback

try:
    with open('VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    nodes = {}
    def find_node(seq, names):
        for node in seq:
            if node.get('name') in names:
                nodes[node['name']] = node
            if 'sequence' in node:
                find_node(node['sequence'], names)
            if 'branches' in node:
                for b in node['branches'].values():
                    find_node(b, names)

    find_node(data.get('sequence', []), ['GPT-4 Analysis', 'GPT-4 Query Data', 'Format Product Info', 'Format Wishlist'])
    
    with open('fixed_nodes.json', 'w', encoding='utf-8') as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)
    print("SUCCESS")
except Exception as e:
    print("ERROR")
