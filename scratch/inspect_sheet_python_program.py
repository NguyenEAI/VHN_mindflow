import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
node = data['sequence'][5]['branches']['b2c_consult'][3]['branches']['true'][0]['sequence'][1]
out.append('Python Program: ' + str(node['properties'].get('program')))

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_sheet_python_program.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
