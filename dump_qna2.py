import json

file_path = r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

def dump_node_instruction(nodes):
    for n in nodes:
        if n.get('id') == '52532d1c2a7a9307df8455e1d70a9c05' and n.get('type') == 'qna':
            with open('final_qna.txt', 'w', encoding='utf-8') as out:
                out.write(n['properties']['instruction'])
            print("Dumped instruction.")
            return True
        if 'branches' in n:
            for b in n['branches'].values():
                if dump_node_instruction(b):
                    return True
        if 'sequence' in n:
            if dump_node_instruction(n['sequence']):
                return True
    return False

dump_node_instruction(data.get('sequence', []))
