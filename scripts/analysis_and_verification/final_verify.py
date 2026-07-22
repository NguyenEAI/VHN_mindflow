"""Final verification: compare all critical nodes between fixing and fixed."""
import json

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_all_nodes(seq):
    results = []
    for node in seq:
        results.append(node)
        if 'sequence' in node:
            results.extend(find_all_nodes(node['sequence']))
        if 'branches' in node:
            for b in node['branches'].values():
                results.extend(find_all_nodes(b))
    return results

fixing = load_json(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_fixing.json')
fixed = load_json(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json')

fixing_nodes = find_all_nodes(fixing.get('sequence', []))
fixed_nodes = find_all_nodes(fixed.get('sequence', []))

print("=" * 60)
print("VERIFICATION CHECKLIST")
print("=" * 60)

# 1. setVar
print("\n1. setVar (session.extra.query_data)")
for n in fixed_nodes:
    if n.get('type') == 'setVar' and n.get('properties', {}).get('varName') == 'session.extra.query_data':
        val = n['properties']['varValue']
        print(f"   [{n.get('name')}] varValue = {val}")
        has_replace = '.replace' in val
        has_curly = '{k:' in val or 'dict(' in val
        if has_replace or has_curly:
            print(f"   *** PROBLEM: Contains .replace() or complex expr! ***")
        else:
            print(f"   OK: Simple json.loads()")

# 2. API body
print("\n2. botAPICall (api_body)")
for n in fixed_nodes:
    if n.get('type') == 'botAPICall' and 'query_data' in n.get('properties', {}).get('api_body', ''):
        body = n['properties']['api_body']
        has_bracket = '[0]' in body
        print(f"   [{n.get('name')}]")
        if has_bracket:
            print(f"   *** PROBLEM: Contains [0] indexing! ***")
        else:
            print(f"   OK: Uses simple .vendor/.product_type")

# 3. json_check
print("\n3. Python json_check")
fixing_check = None
fixed_check = None
for n in fixing_nodes:
    if n.get('type') == 'python' and n.get('properties', {}).get('varName') == 'json_check':
        fixing_check = n['properties']['expression']
for n in fixed_nodes:
    if n.get('type') == 'python' and n.get('properties', {}).get('varName') == 'json_check':
        fixed_check = n['properties']['expression']

if fixing_check and fixed_check:
    if fixing_check.strip() == fixed_check.strip():
        print("   OK: json_check MATCHES VHN_fixing.json exactly!")
    else:
        print("   *** PROBLEM: json_check DIFFERS from VHN_fixing.json! ***")
        # Show diff
        f1 = fixing_check.strip().split('\n')
        f2 = fixed_check.strip().split('\n')
        for i, (l1, l2) in enumerate(zip(f1, f2)):
            if l1 != l2:
                print(f"   Line {i+1} FIXING: {l1}")
                print(f"   Line {i+1} FIXED:  {l2}")

# 4. Check for dangerous chars in all setVar varValues
print("\n4. Check ALL setVar nodes for Handlebars-unsafe chars")
for n in fixed_nodes:
    if n.get('type') == 'setVar':
        val = n.get('properties', {}).get('varValue', '')
        issues = []
        if '{k:' in val: issues.append('dict comprehension {k:}')
        if '.replace(' in val: issues.append('.replace() chain')
        if 'dict(' in val: issues.append('dict() call')
        if issues:
            print(f"   *** [{n.get('name')}] UNSAFE: {', '.join(issues)}")
            print(f"       Value: {val}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
