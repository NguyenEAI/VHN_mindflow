import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
node = data['sequence'][12]['sequence'][0]['branches']['true'][0]['sequence'][2]['branches']['true'][0]
out.append('Original Var [session.extra.query_data] in VHN_fixing.json:')
out.append('varValue: ' + repr(node.get('properties', {}).get('varValue')))

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_fixing_query.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
