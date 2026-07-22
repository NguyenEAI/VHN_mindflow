import json

file_path = r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

def dump_nodes(nodes, out):
    for n in nodes:
        if n.get('type') == 'botAPICall':
            out.write(json.dumps(n, ensure_ascii=False, indent=2) + '\n')
        if 'branches' in n:
            for b in n['branches'].values():
                dump_nodes(b, out)
        if 'sequence' in n:
            dump_nodes(n['sequence'], out)

with open('api_node.txt', 'w', encoding='utf-8') as f:
    dump_nodes(data.get('sequence', []), f)
print("Dumped to api_node.txt")
