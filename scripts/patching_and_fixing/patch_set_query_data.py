import json

def patch_set_query_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    patched = 0
    def traverse(seq):
        nonlocal patched
        for node in seq:
            if node.get('type') == 'setVar' and node.get('properties', {}).get('varName') == 'session.extra.query_data':
                if 'replace' not in node['properties'].get('varValue', ''):
                    node['properties']['varValue'] = "json.loads(bot_json_query.replace('```json', '').replace('```', ''))"
                    patched += 1
                        
            if 'sequence' in node:
                traverse(node['sequence'])
            if 'branches' in node:
                for b in node['branches'].values():
                    traverse(b)
                    
    traverse(data.get('sequence', []))
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Patched {patched} setVar nodes.")

patch_set_query_data(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json')
