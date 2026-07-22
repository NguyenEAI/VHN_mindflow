import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# The sequence inside b2c_consult
sheet_product = data['sequence'][5]['branches']['b2c_consult'][3]['branches']['true'][0]
seq = sheet_product['sequence']

# 1. Fix the Save findproduct_data node
# Path: [4, 'branches', 'true', 6]
bad_node = seq[4]['branches']['true'][6]
if bad_node.get('name') == 'Save findproduct_data':
    bad_node['properties']['varValue'] = "session.extra.product_information"
    print("Fixed Save findproduct_data!")

# 2. Fix the query_data parsing
# Path to `If json_check == "Yes"` is seq[2]. Its true branch:
true_branch = seq[2]['branches']['true']

# We will replace true_branch[0] which is `Var [session.extra.query_data]`
# with TWO nodes:
#   a) a Python node to clean the string
#   b) a setVar node to load the JSON

clean_node = {
    "id": "clean_bot_json_query",
    "name": "Clean bot_json_query",
    "type": "python",
    "componentType": "task",
    "properties": {
        "varName": "session.extra.clean_query",
        "expression": 'q = """{{bot_json_query}}"""\nprint(q.replace("json", "").replace("```", "").strip())'
    }
}

setvar_node = {
    "id": "set_query_data",
    "name": "Var [session.extra.query_data]",
    "type": "setVar",
    "componentType": "task",
    "properties": {
        "varName": "session.extra.query_data",
        "varValue": "json.loads(session.extra.clean_query)"
    }
}

# We replace the first node with these two
if true_branch[0].get('name') == 'Var [session.extra.query_data]':
    # insert at index 0 and 1
    true_branch.pop(0)
    true_branch.insert(0, clean_node)
    true_branch.insert(1, setvar_node)
    print("Fixed Var [session.extra.query_data]!")

# 3. Just to be absolutely safe, check for any remaining `{{` in varValues
def fix_braces(nodes):
    for node in nodes:
        if node.get('type') == 'setVar':
            val = str(node.get('properties', {}).get('varValue', ''))
            if val.startswith('{{') and val.endswith('}}'):
                node['properties']['varValue'] = val[2:-2].strip()
                print(f"Removed braces from {node.get('name')}")
        if 'sequence' in node:
            fix_braces(node['sequence'])
        if 'branches' in node:
            for b in node['branches'].values():
                fix_braces(b)

fix_braces(data.get('sequence', []))

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Saved VHN_DauTien_Fixed.json successfully!")
