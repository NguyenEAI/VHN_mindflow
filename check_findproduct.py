import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def find_node(seq, name):
    for node in seq:
        if node.get('name') == name:
            return True
        if 'sequence' in node:
            if find_node(node['sequence'], name): return True
        if 'branches' in node:
            for b in node['branches'].values():
                if find_node(b, name): return True
    return False

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
    
has_node = find_node(data.get('sequence', []), 'Save findproduct_data')

if not has_node:
    print("Save findproduct_data not found, injecting it...")
    # Find the true branch of 'Have results?' and inject at the end
    have_results = get_node(data.get('sequence', []), 'Have results?')
    if have_results and 'branches' in have_results and 'true' in have_results['branches']:
        true_branch = have_results['branches']['true']
        true_branch.append({
            "id": "setVar_save_findproduct_data_999",
            "name": "Save findproduct_data",
            "type": "setVar",
            "properties": {
                "varName": "session.extra.findproduct_data",
                "varValue": "{{ session.extra.product_information }}"
            }
        })
        with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Injected.")
else:
    print("Save findproduct_data ALREADY EXISTS.")
