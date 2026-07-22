"""Final comprehensive verification after hallucination fix."""
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
print("FINAL VERIFICATION")
print("=" * 60)

# 1. GPT-4 Query Data instruction
print("\n1. GPT-4 Query Data instruction (B2C)")
fixing_inst = None
fixed_inst = None
for n in fixing_nodes:
    if n.get('id') == '52532d1c2a7a9307df8455e1d70a9c05':
        fixing_inst = n['properties']['instruction']
for n in fixed_nodes:
    if n.get('id') == '52532d1c2a7a9307df8455e1d70a9c05':
        fixed_inst = n['properties']['instruction']

if fixing_inst == fixed_inst:
    print("   OK: MATCHES VHN_fixing.json EXACTLY!")
else:
    print("   PROBLEM: Instructions differ!")
    # Find first difference
    for i, (c1, c2) in enumerate(zip(fixing_inst, fixed_inst)):
        if c1 != c2:
            print(f"   First diff at char {i}:")
            print(f"   fixing: ...{fixing_inst[max(0,i-20):i+20]}...")
            print(f"   fixed:  ...{fixed_inst[max(0,i-20):i+20]}...")
            break

# 2. setVar
print("\n2. setVar (session.extra.query_data)")
for n in fixed_nodes:
    if n.get('type') == 'setVar' and n.get('properties', {}).get('varName') == 'session.extra.query_data':
        val = n['properties']['varValue']
        ok = val in ('json.loads(bot_json_query)', 'json.loads(ai_query_data)')
        print(f"   [{n.get('name')}] = {val} {'OK' if ok else 'PROBLEM!'}")

# 3. API body
print("\n3. API body")
for n in fixed_nodes:
    if n.get('type') == 'botAPICall' and 'query_data' in n.get('properties', {}).get('api_body', ''):
        body = n['properties']['api_body']
        has_bracket = '[0]' in body
        print(f"   [{n.get('name')}] {'PROBLEM: has [0]' if has_bracket else 'OK: no [0]'}")

# 4. json_check
print("\n4. Python json_check")
for label, nodes in [("fixing", fixing_nodes), ("fixed", fixed_nodes)]:
    for n in nodes:
        if n.get('type') == 'python' and n.get('properties', {}).get('varName') == 'json_check':
            expr = n['properties']['expression']
            has_markdown_strip = '```json' in expr
            print(f"   {label}: has_markdown_strip={has_markdown_strip}, len={len(expr)}")

# 5. Format Product Info - robust matching
print("\n5. Format Product Info matching")
for n in fixed_nodes:
    if n.get('type') == 'python' and n.get('properties', {}).get('varName') == 'session.extra.product_information':
        expr = n['properties']['expression']
        uses_handlebars = '{{' in expr
        uses_exact = 'title == names' in expr
        uses_substring = 'names_lower in title_lower' in expr
        print(f"   [{n.get('name')}]")
        print(f"     Handlebars template: {uses_handlebars}")
        print(f"     Exact match (==): {uses_exact}")
        print(f"     Substring match (in): {uses_substring}")
        if uses_substring:
            print(f"     OK: Robust matching!")
        elif uses_exact:
            print(f"     WARNING: Exact match only - may fail for long names!")

# 6. Format Wishlist
print("\n6. Format Wishlist")
for n in fixed_nodes:
    if n.get('type') == 'python' and n.get('properties', {}).get('varName') == 'session.extra.product_wishlist':
        expr = n['properties']['expression']
        uses_handlebars = '{{' in expr
        print(f"   [{n.get('name')}] Handlebars: {uses_handlebars}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
