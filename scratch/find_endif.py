import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.finditer(r'\{\{/if\}\}', text)
out = []
for m in matches:
    idx = m.start()
    out.append('Found {{/if}} at ' + str(idx))
    out.append(text[max(0, idx-100):min(len(text), idx+100)])

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\find_endif.txt', 'w', encoding='utf-8') as f:
    if out:
        f.write('\n'.join(out))
    else:
        f.write('Not found\n')
