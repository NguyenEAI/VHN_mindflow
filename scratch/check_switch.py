import json, codecs

for fname in ['VHN_DauTien.json', 'VHN_DauTien_Fixed.json']:
    with codecs.open(f'c:/Users/Administrator/Desktop/Hoc_python/{fname}', 'r', 'utf-8') as f:
        d = json.load(f)
    for n in d.get('sequence', []):
        if n.get('type') == 'flowSwitch':
            has_branches = 'branches' in n
            has_prop_branches = 'branches' in n.get('properties', {})
            has_conditions = 'conditions' in n.get('properties', {})
            print(f'{fname}: root.branches={has_branches}, props.branches={has_prop_branches}, props.conditions={has_conditions}')
            if has_branches:
                print(f'  Root branches keys: {sorted(n["branches"].keys())}')
            if has_prop_branches:
                print(f'  Props branches keys: {sorted(n["properties"]["branches"].keys())}')
