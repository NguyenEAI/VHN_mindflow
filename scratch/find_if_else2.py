import re

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\simulate_hbs.txt', 'r', encoding='utf-8') as f:
    text = f.read()

matches = re.finditer(r'\{\{/if\}\}\n\{\{else\}\}', text)
out = []
for m in matches:
    idx = m.start()
    out.append('Found at ' + str(idx))
    out.append(text[max(0, idx-100):min(len(text), idx+100)])

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\find_if_else2.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
