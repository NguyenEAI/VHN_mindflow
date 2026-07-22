import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

n4 = data['sequence'][4]
out = []
out.append('Branches: ' + str(list(n4.get('branches', {}).keys())))
if 'false' in n4.get('branches', {}):
    for child in n4['branches']['false']:
        out.append('  False child: ' + str(child.get('name')))

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_n4_false.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
