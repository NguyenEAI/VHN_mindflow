import json

def patch_vhn(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    set_vars_patched = 0
    api_calls_patched = 0
    
    def traverse(seq):
        nonlocal set_vars_patched, api_calls_patched
        for node in seq:
            if node.get('type') == 'setVar' and node.get('properties', {}).get('varName') == 'session.extra.query_data':
                node['properties']['varValue'] = "{k: (v[0] if isinstance(v, list) and len(v)>0 else v) for k, v in json.loads(bot_json_query.replace('```json', '').replace('```', '')).items()}"
                set_vars_patched += 1
                
            if node.get('type') == 'botAPICall' and 'api_body' in node.get('properties', {}):
                api_body = node['properties']['api_body']
                if 'session.extra.query_data.vendor[0]' in api_body:
                    node['properties']['api_body'] = api_body.replace('session.extra.query_data.vendor[0]', 'session.extra.query_data.vendor')
                    node['properties']['api_body'] = node['properties']['api_body'].replace('session.extra.query_data.product_type[0]', 'session.extra.query_data.product_type')
                    api_calls_patched += 1
                        
            if 'sequence' in node:
                traverse(node['sequence'])
            if 'branches' in node:
                for b in node['branches'].values():
                    traverse(b)
                    
    traverse(data.get('sequence', []))
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Patched {set_vars_patched} setVar nodes and {api_calls_patched} API Call nodes.")

patch_vhn(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json')
