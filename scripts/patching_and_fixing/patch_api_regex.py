import json
import re

def patch_api_body(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    patched = 0
    
    def traverse(seq):
        nonlocal patched
        for node in seq:
            if node.get('type') == 'botAPICall' and 'api_body' in node.get('properties', {}):
                api_body = node['properties']['api_body']
                new_body = re.sub(r'session\.extra\.query_data\.vendor\s*\}\}', r'session.extra.query_data.vendor[0] }}', api_body)
                new_body = re.sub(r'session\.extra\.query_data\.product_type\s*\}\}', r'session.extra.query_data.product_type[0] }}', new_body)
                
                if new_body != api_body:
                    node['properties']['api_body'] = new_body
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

patch_api_body(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json')
