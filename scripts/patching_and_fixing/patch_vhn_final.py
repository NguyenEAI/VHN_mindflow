import json

def patch_vhn(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    set_vars_patched = 0
    instructions_patched = 0
    api_calls_patched = 0
    
    def traverse(seq):
        nonlocal set_vars_patched, instructions_patched, api_calls_patched
        for node in seq:
            # Patch Set query_data (B2C)
            if node.get('type') == 'setVar' and node.get('properties', {}).get('varName') == 'session.extra.query_data':
                if node.get('name') == 'Set Query': # B2B
                    node['properties']['varValue'] = "json.loads(ai_query_data.replace('```json','').replace('```',''))"
                    set_vars_patched += 1
                else: # B2C
                    node['properties']['varValue'] = "json.loads(bot_json_query.replace('```json','').replace('```',''))"
                    set_vars_patched += 1
                        
            # Patch GPT-4 Query Data prompt
            if node.get('name') == 'GPT-4 Query Data' and 'instruction' in node.get('properties', {}):
                inst = node['properties']['instruction']
                if 'có thể là 1 giá trị' in inst:
                    inst = inst.replace('có thể là 1 giá trị, hoặc là array các giá trị (ví dụ: "vendor": "none" or "vendor": ["christina", "floslek"])', 'phải là array (ví dụ: "vendor": ["none"] hoặc "vendor": ["christina", "floslek"])')
                    inst = inst.replace('có thể là 1 giá trị, hoặc là array các giá trị (ví dụ: "product_type": "none" or "product_type": ["serum", "cleanser", "toner"])', 'phải là array (ví dụ: "product_type": ["none"] hoặc "product_type": ["serum", "cleanser", "toner"])')
                    inst = inst.replace('Giá trị mặc định ban đầu của "vendor" là "none"', 'Giá trị mặc định ban đầu của "vendor" là ["none"]')
                    inst = inst.replace('Giá trị mặc định ban đầu của "product_type" là "none"', 'Giá trị mặc định ban đầu của "product_type" là ["none"]')
                    node['properties']['instruction'] = inst
                    instructions_patched += 1
                    
            # Patch API CALL PRODUCT DATA to use [0]
            if node.get('type') == 'botAPICall' and 'api_body' in node.get('properties', {}):
                api_body = node['properties']['api_body']
                if 'session.extra.query_data.vendor"' in api_body:
                    node['properties']['api_body'] = api_body.replace('session.extra.query_data.vendor"', 'session.extra.query_data.vendor[0]"')
                    node['properties']['api_body'] = node['properties']['api_body'].replace('session.extra.query_data.product_type"', 'session.extra.query_data.product_type[0]"')
                    api_calls_patched += 1
                    
            if 'sequence' in node:
                traverse(node['sequence'])
            if 'branches' in node:
                for b in node['branches'].values():
                    traverse(b)
                    
    traverse(data.get('sequence', []))
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Patched {set_vars_patched} setVar nodes.")
    print(f"Patched {instructions_patched} instruction nodes.")
    print(f"Patched {api_calls_patched} API Call nodes.")

patch_vhn(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json')
