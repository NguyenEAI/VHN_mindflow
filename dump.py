import json

file_path = r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for node in data.get('sequence', []):
    if node.get('type') == 'flowSwitch':
        for b in node.get('branches', {}).get('b2c_consult', []):
            if b.get('type') == 'qna' and b.get('name') == 'AI QnA B2C Consult' or b.get('id') == '8a045fd50c088e3adf5f000f40c21d66':
                with open('prompt_dump.txt', 'w', encoding='utf-8') as out:
                    out.write(b['properties']['instruction'])
                print('Found and dumped to prompt_dump.txt')
