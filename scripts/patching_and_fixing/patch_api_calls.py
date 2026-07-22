import json

def patch_api_calls(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    patched = 0
    def traverse(seq):
        nonlocal patched
        for node in seq:
            if node.get('type') == 'botAPICall' and 'api_body' in node.get('properties', {}):
                api_body = node['properties']['api_body']
                # If it contains session.extra.query_data.vendor without [0]
                if 'session.extra.query_data.vendor"' in api_body or 'session.extra.query_data.vendor }' in api_body:
                    if 'vendor[0]' not in api_body:
                        node['properties']['api_body'] = api_body.replace('session.extra.query_data.vendor', 'session.extra.query_data.vendor[0]')
                        node['properties']['api_body'] = node['properties']['api_body'].replace('session.extra.query_data.product_type', 'session.extra.query_data.product_type[0]')
                        patched += 1
                        
            if 'sequence' in node:
                traverse(node['sequence'])
            if 'branches' in node:
                for b in node['branches'].values():
                    traverse(b)
                    
    traverse(data.get('sequence', []))
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Patched {patched} API Call nodes.")

patch_api_calls(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json')
