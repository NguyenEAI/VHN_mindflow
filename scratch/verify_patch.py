import json

with open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    text = f.read()

if 'tẩy tế bào chết' in text:
    idx = text.find('tẩy tế bào chết')
    start = max(0, idx - 100)
    end = min(len(text), idx + 100)
    print("Found! Context:")
    print(text[start:end])
else:
    print("Not found.")
