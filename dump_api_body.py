import json

file_path = r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

def dump_api_body(nodes):
    for n in nodes:
        if n.get('id') == '3173e7d6fcbdeb4100c4dfabad2c1bbd':
            with open('api_body.txt', 'w', encoding='utf-8') as out:
                out.write(n['properties']['api_body'])
            return True
        if 'branches' in n:
            for b in n['branches'].values():
                if dump_api_body(b): return True
        if 'sequence' in n:
            if dump_api_body(n['sequence']): return True
    return False

dump_api_body(data.get('sequence', []))
