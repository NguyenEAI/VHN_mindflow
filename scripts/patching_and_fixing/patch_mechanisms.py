import json

with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes = {}
def find_node(seq):
    for node in seq:
        if node.get('id') in ['52532d1c2a7a9307df8455e1d70a9c05', 'fb5a13c13db9c1499f374e20e623e775', '6d3f02d97dab85e491a60d076f675a58']:
            nodes[node['id']] = node
        if 'sequence' in node:
            find_node(node['sequence'])
        if 'branches' in node:
            for b in node['branches'].values():
                find_node(b)

find_node(data.get('sequence', []))

with open('VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    fixed_data = json.load(f)

def apply_node(seq):
    changed = False
    for node in seq:
        if node.get('id') in nodes:
            node['properties'] = nodes[node['id']]['properties']
            changed = True
            print(f"Updated {node.get('name')} ({node.get('id')})")
        if 'sequence' in node:
            if apply_node(node['sequence']): changed = True
        if 'branches' in node:
            for b in node['branches'].values():
                if apply_node(b): changed = True
    return changed

if apply_node(fixed_data.get('sequence', [])):
    with open('VHN_DauTien_Fixed.json', 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)
    print('PATCHED')
