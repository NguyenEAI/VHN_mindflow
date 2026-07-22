import re

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\simulate_hbs.txt', 'r', encoding='utf-8') as f:
    text = f.read()

matches = re.finditer(r'\{\{/if\}\}\n\{\{else\}\}', text)
out = []
for m in matches:
    idx = m.start()
    out.append('Found {{/if}} followed by {{else}} at ' + str(idx))

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\find_if_else.txt', 'w', encoding='utf-8') as f:
    if out:
        f.write('\n'.join(out))
    else:
        f.write('Not found\n')
