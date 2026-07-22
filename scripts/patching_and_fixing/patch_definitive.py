"""
DEFINITIVE FIX: Revert setVar and API body to match VHN_fixing.json EXACTLY.

Root cause analysis:
1. Mindflow compiles setVar.varValue into a Handlebars {{ set ... }} expression.
2. Handlebars parser does NOT support Python method chains like .replace().
3. The Python json_check node ALREADY strips markdown from bot_json_query
   BEFORE the setVar node runs. So .replace() is REDUNDANT and HARMFUL.
4. VHN_fixing.json uses simple `json.loads(bot_json_query)` — this works.
5. API body uses `{{ session.extra.query_data.vendor }}` without [0] — this works
   because GPT-4 with json_mode returns strings, not arrays, after json_check validates.

Fix:
- setVar B2C: json.loads(bot_json_query)     [EXACTLY like VHN_fixing.json]
- setVar B2B: json.loads(ai_query_data)       [EXACTLY like VHN_fixing.json pattern]
- API body:   session.extra.query_data.vendor  [NO [0], EXACTLY like VHN_fixing.json]
"""
import json

def fix_vhn(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    fixes = {'setVar': 0, 'apiBody': 0}
    
    def traverse(seq):
        for node in seq:
            # Fix 1: Revert setVar to simple json.loads() 
            if node.get('type') == 'setVar' and node.get('properties', {}).get('varName') == 'session.extra.query_data':
                old_val = node['properties']['varValue']
                if node.get('name') == 'Set Query':  # B2B path
                    node['properties']['varValue'] = 'json.loads(ai_query_data)'
                else:  # B2C path (Set query_data)
                    node['properties']['varValue'] = 'json.loads(bot_json_query)'
                if old_val != node['properties']['varValue']:
                    fixes['setVar'] += 1
                    print(f"  setVar [{node.get('name')}]: '{old_val}' -> '{node['properties']['varValue']}'")
            
            # Fix 2: Revert API body to use vendor/product_type WITHOUT [0]
            if node.get('type') == 'botAPICall' and 'api_body' in node.get('properties', {}):
                old_body = node['properties']['api_body']
                new_body = old_body.replace('session.extra.query_data.vendor[0]', 'session.extra.query_data.vendor')
                new_body = new_body.replace('session.extra.query_data.product_type[0]', 'session.extra.query_data.product_type')
                if new_body != old_body:
                    node['properties']['api_body'] = new_body
                    fixes['apiBody'] += 1
                    print(f"  apiBody [{node.get('name')}]: removed [0] indexing")
            
            if 'sequence' in node:
                traverse(node['sequence'])
            if 'branches' in node:
                for b in node['branches'].values():
                    traverse(b)
    
    traverse(data.get('sequence', []))
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nTotal: {fixes['setVar']} setVar fixed, {fixes['apiBody']} apiBody fixed.")

print("Applying definitive fix to VHN_DauTien_Fixed.json...")
fix_vhn(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json')
