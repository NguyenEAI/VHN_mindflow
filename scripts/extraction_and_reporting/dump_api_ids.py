import json

with open('VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes = []
def find_node(seq):
    for node in seq:
        if node.get('name') in ['API CALL PRODUCT DATA', 'API CALL PRODUCT DATA FALLBACK']:
            nodes.append({ 'name': node['name'], 'id': node['id'], 'properties': node.get('properties', {}) })
        if 'sequence' in node:
            find_node(node['sequence'])
        if 'branches' in node:
            for b in node['branches'].values():
                find_node(b)

find_node(data.get('sequence', []))
with open('api_call_ids.json', 'w', encoding='utf-8') as f:
    json.dump(nodes, f, ensure_ascii=False, indent=2)
