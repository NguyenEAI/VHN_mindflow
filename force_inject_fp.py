import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def get_node(seq, name):
    for node in seq:
        if node.get('name') == name:
            return node
        if 'sequence' in node:
            res = get_node(node['sequence'], name)
            if res: return res
        if 'branches' in node:
            for b in node['branches'].values():
                res = get_node(b, name)
                if res: return res
    return None

have_results = get_node(data.get('sequence', []), 'Have results?')
if have_results and 'branches' in have_results and 'true' in have_results['branches']:
    true_branch = have_results['branches']['true']
    
    # Check if Save findproduct_data is already in this branch
    already_exists = any(n.get('name') == 'Save findproduct_data' for n in true_branch)
    if not already_exists:
        true_branch.append({
            "id": "setVar_save_findproduct_data_999",
            "name": "Save findproduct_data",
            "type": "setVar",
            "componentType": "task",
            "properties": {
                "varName": "session.extra.findproduct_data",
                "varValue": "{{ session.extra.product_information }}"
            }
        })
        print("Injected Save findproduct_data")
        with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        print("Already exists in true branch")
else:
    print("Could not find Have results?")
