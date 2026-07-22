import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
node = data['sequence'][5]['branches']['b2c_consult'][3]['branches']['true'][0]
def search_node(seq, path=[]):
    for i, n in enumerate(seq):
        out.append(str(path + [i]) + ': ' + str(n.get('name')) + ' (' + str(n.get('type')) + ')')
        if 'sequence' in n:
            search_node(n['sequence'], path + [i, 'sequence'])
        if 'branches' in n:
            for b_name, b_seq in n['branches'].items():
                search_node(b_seq, path + [i, 'branches', b_name])

search_node(node.get('sequence', []))
with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_sheet_all.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
