import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
def search_node(seq):
    for node in seq:
        props = node.get('properties', {})
        for k, v in props.items():
            if isinstance(v, str) and 'n)' in v:
                out.append(f"Found 'n)' in node {node.get('name')} (type {node.get('type')}) prop {k}: {v[-50:]}")
            if isinstance(v, str) and '}' in v:
                # specifically look for unbalanced braces
                open_braces = v.count('{')
                close_braces = v.count('}')
                if open_braces != close_braces:
                    out.append(f"Unbalanced braces in node {node.get('name')} prop {k}: {open_braces} open, {close_braces} close")
        if 'sequence' in node:
            search_node(node['sequence'])
        if 'branches' in node:
            for b in node['branches'].values():
                search_node(b)

search_node(data.get('sequence', []))
with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\search_n.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
