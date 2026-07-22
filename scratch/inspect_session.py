import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
session_manager_extra = json.loads(data['sequence'][0]['properties']['extra'])
out.append('Keys in Session Manager extra:')
for k in session_manager_extra.keys():
    out.append(k)

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_session.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
