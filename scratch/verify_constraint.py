import json, codecs, sys

sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
    data = json.load(f)

for n in data.get('sequence', []):
    if n.get('type') == 'flowSwitch':
        for b in n.get('branches', {}).get('b2c_consult', []):
            if b.get('type') == 'qna' and 'B2C' in b.get('name', ''):
                inst = b.get('properties', {}).get('instruction', '')
                print(f"Node Name: {b.get('name')}")
                print(f"Instruction length: {len(inst)}")
                if 'KHÔNG TỰ Ý ĐỀ XUẤT CÁC BƯỚC KHÁC' in inst:
                    print("Constraint FOUND!")
                else:
                    print("Constraint NOT FOUND!")
