import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def get_node(seq, name):
    for node in seq:
        if node.get('name') == name:
            return node
        if 'sequence' in node:
            res = get_node(node['sequence'], name)
            if res: return res
        if 'branches' in node:
            for b in node['branches'].values():
                res = get_node(b, name)
                if res: return res
    return None
    
node = get_node(data.get('sequence', []), 'Format Product Info')
with open('fpi_check.txt', 'w', encoding='utf-8') as f:
    if node:
        f.write('Type: ' + str(node.get('type')) + '\n')
        f.write('VarName: ' + str(node.get('properties', {}).get('varName')) + '\n')
        f.write('Expression: ' + str(node.get('properties', {}).get('expression'))[:100] + '...\n')
    else:
        f.write('Not found\n')
