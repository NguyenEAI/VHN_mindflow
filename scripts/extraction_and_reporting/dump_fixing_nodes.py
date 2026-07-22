import json
with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
nodes = []
def find_node(seq):
    for node in seq:
        name = node.get('name')
        if name in ['GPT-4 Query Data', 'Python json_check', 'Set query_data', 'API CALL PRODUCT DATA', 'Python python_check', 'Set api_body_raw']:
            nodes.append(node)
        if 'sequence' in node:
            find_node(node['sequence'])
        if 'branches' in node:
            for b in node['branches'].values():
                find_node(b)
find_node(data.get('sequence', []))
with open('dump_fixing_nodes.json', 'w', encoding='utf-8') as f:
    json.dump(nodes, f, ensure_ascii=False, indent=2)
