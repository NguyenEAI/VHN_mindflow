import json
with open('VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
out = ""
def find_node(seq):
    global out
    for node in seq:
        if node.get('name') == 'Python json_check':
            out += 'ID: ' + node.get('id', '') + '\n'
            out += 'Expr: ' + node.get('properties', {}).get('expression', '') + '\n\n'
        if 'sequence' in node:
            find_node(node['sequence'])
        if 'branches' in node:
            for b in node['branches'].values():
                find_node(b)
find_node(data.get('sequence', []))
with open('dump_json_check_expr.txt', 'w', encoding='utf-8') as f:
    f.write(out)
