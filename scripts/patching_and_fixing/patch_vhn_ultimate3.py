import json

def patch_vhn(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    set_vars_patched = 0
    
    def traverse(seq):
        nonlocal set_vars_patched
        for node in seq:
            if node.get('type') == 'setVar' and node.get('properties', {}).get('varName') == 'session.extra.query_data':
                if node.get('name') == 'Set Query': # B2B
                    node['properties']['varValue'] = "dict((k, v[0] if isinstance(v, list) and len(v)>0 else v) for k, v in json.loads(ai_query_data.replace('```json', '').replace('```', '')).items())"
                    set_vars_patched += 1
                else: # B2C
                    node['properties']['varValue'] = "dict((k, v[0] if isinstance(v, list) and len(v)>0 else v) for k, v in json.loads(bot_json_query.replace('```json', '').replace('```', '')).items())"
                    set_vars_patched += 1
                        
            if 'sequence' in node:
                traverse(node['sequence'])
            if 'branches' in node:
                for b in node['branches'].values():
                    traverse(b)
                    
    traverse(data.get('sequence', []))
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Patched {set_vars_patched} setVar nodes.")

patch_vhn(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json')
