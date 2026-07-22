import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
def search_node(seq):
    for node in seq:
        if node.get('type') == 'python':
            code = str(node.get('properties', {}).get('code', ''))
            if '{{' in code or '}}' in code:
                out.append('Found braces in Python node: ' + str(node.get('name')))
        if 'sequence' in node:
            search_node(node['sequence'])
        if 'branches' in node:
            for b in node['branches'].values():
                search_node(b)

search_node(data.get('sequence', []))
with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_python_braces.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
