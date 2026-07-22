import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.finditer(r'"varValue"\s*:\s*"empty_str\(\)"', text)
out = []
for m in matches:
    idx = m.start()
    out.append('Found empty_str() at ' + str(idx))
    out.append(text[max(0, idx-1000):min(len(text), idx+100)])

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\find_empty_str.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
