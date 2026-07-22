"""
Revert json_check to match VHN_fixing.json EXACTLY.
Since json_mode: true is enabled on the QnA node, GPT-4 always returns
pure JSON without markdown wrapping. If somehow it does wrap markdown,
json.loads() will fail and json_check = "No" -> fallback path runs.
This is the EXACT behavior of VHN_fixing.json.
"""
import json

FIXING_JSON_CHECK_EXPRESSION = """import json

QUERY = \"\"\"{{bot_json_query}}\"\"\"
KEYS = ["vendor", "product_type"]
VENDOR = ["christina", "dermoaroma", "floslek", "ivatherm", "pharmalife", "preime", "none"]
PRODUCT_TYPE = ["antisun", "body", "cleanser", "cream", "kit", "mask", "micellar", "peel", "serum", "supply", "toner", "exfoliate", "others", "inject", "foam", "none"]

if type(QUERY).__name__ == 'str':
    try:
        parsed_data = json.loads(QUERY)
        unique_keys_to_check = set(KEYS)
        missing_keys = []
        result_vendor = False
        result_type = False

        for keys in unique_keys_to_check:
            if keys not in parsed_data:
                missing_keys.append(keys)

        if not missing_keys: 
            vendor_value = parsed_data["vendor"]
            type_value = parsed_data["product_type"]

            for key in VENDOR:
                if key in vendor_value:
                    result_vendor = True
                    break

            for key in PRODUCT_TYPE:
                if key in type_value:
                    result_type = True
                    break

            if result_vendor and result_type:
                print("Yes")
        else:
            print("No")
    except json.JSONDecodeError:
        print("No")
else:
    print("No")"""

def fix_vhn(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    fixed = 0
    
    def traverse(seq):
        nonlocal fixed
        for node in seq:
            if node.get('type') == 'python' and node.get('properties', {}).get('varName') == 'json_check':
                old_expr = node['properties']['expression']
                node['properties']['expression'] = FIXING_JSON_CHECK_EXPRESSION
                if old_expr != FIXING_JSON_CHECK_EXPRESSION:
                    fixed += 1
                    print(f"  Reverted json_check node [{node.get('name')}]")
            
            if 'sequence' in node:
                traverse(node['sequence'])
            if 'branches' in node:
                for b in node['branches'].values():
                    traverse(b)
    
    traverse(data.get('sequence', []))
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nTotal: {fixed} json_check nodes reverted.")

print("Reverting json_check to VHN_fixing.json version...")
fix_vhn(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json')
