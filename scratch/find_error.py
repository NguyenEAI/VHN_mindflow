import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('n) }}')
with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\find_error.txt', 'w', encoding='utf-8') as f:
    if idx != -1:
        f.write('Found n) }} at ' + str(idx) + '\n')
        f.write(text[max(0, idx-100):min(len(text), idx+100)])
    else:
        f.write('Not found\n')
