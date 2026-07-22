import json

with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes = {}
def find_nodes(seq):
    for node in seq:
        if node.get('name') in ['API CALL PRODUCT DATA', 'Format Product Info', 'GPT-4 Query Data', 'GPT-4 Analysis']:
            nodes[node['name']] = node
        if 'sequence' in node:
            find_nodes(node['sequence'])
        if 'branches' in node:
            for b in node['branches'].values():
                find_nodes(b)

find_nodes(data.get('sequence', []))

with open('fixing_mechanisms.json', 'w', encoding='utf-8') as f:
    json.dump(nodes, f, ensure_ascii=False, indent=2)
