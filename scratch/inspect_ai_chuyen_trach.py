import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
node = data['sequence'][5]['branches']['b2c_consult'][4]
out.append('Instruction: ' + str(node['properties']['instruction']))

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_ai_chuyen_trach.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
