import json

file_path = r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

def dump_nodes(nodes, out, indent=''):
    for n in nodes:
        out.write(f"{indent}ID: {n.get('id')}, Type: {n.get('type')}, Name: {n.get('name')}\n")
        if n.get('type') in ['qna', 'api', 'python', 'setVar']:
            out.write(f"{indent}Properties: {json.dumps(n.get('properties', {}), ensure_ascii=False, indent=2)}\n")
        if 'branches' in n:
            for b_name, b_nodes in n['branches'].items():
                out.write(f"{indent}Branch: {b_name}\n")
                dump_nodes(b_nodes, out, indent + '  ')
        if 'sequence' in n:
            out.write(f"{indent}Sequence:\n")
            dump_nodes(n['sequence'], out, indent + '  ')

for node in data.get('sequence', []):
    if node.get('type') == 'flowSwitch':
        with open('b2c_nodes.txt', 'w', encoding='utf-8') as out:
            b2c_nodes = node.get('branches', {}).get('b2c_consult', [])
            dump_nodes(b2c_nodes, out)
        print('Dumped recursively to b2c_nodes.txt')
