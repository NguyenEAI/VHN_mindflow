import json

file_path = r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for node in data.get('sequence', []):
    if node.get('type') == 'flowSwitch':
        for b in node.get('branches', {}).get('b2c_consult', []):
            if b.get('id') == '74c854c870ce55b3f2c87b2f89311641':
                for seq in b.get('sequence', []):
                    if seq.get('id') == '52532d1c2a7a9307df8455e1d70a9c05':
                        with open('prompt_qna.txt', 'w', encoding='utf-8') as out:
                            out.write(seq['properties']['instruction'])
                        print('Dumped prompt to prompt_qna.txt')
