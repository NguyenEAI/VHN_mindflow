"""Compare VHN_fixing.json structure with VHN_Optimized_Combined.json"""
import json, re

# Load both files
fixing = json.load(open('VHN_fixing.json', encoding='utf-8'))
combined = json.load(open('VHN_Optimized_Combined.json', encoding='utf-8'))

# Get all component types used in VHN_fixing
def get_all_types(obj):
    types = set()
    if isinstance(obj, dict):
        if 'type' in obj:
            types.add(obj['type'])
        for v in obj.values():
            types.update(get_all_types(v))
    elif isinstance(obj, list):
        for item in obj:
            types.update(get_all_types(item))
    return types

print("=== VHN_fixing component types ===")
fixing_types = sorted(get_all_types(fixing))
for t in fixing_types:
    print(f"  {t}")

print("\n=== VHN_Optimized_Combined component types ===")
combined_types = sorted(get_all_types(combined))
for t in combined_types:
    print(f"  {t}")

print(f"\nTypes in combined but NOT in fixing: {set(combined_types) - set(fixing_types)}")
print(f"Types in fixing but NOT in combined: {set(fixing_types) - set(combined_types)}")

# Check how VHN_fixing handles product queries
print("\n=== VHN_fixing: How it handles product search ===")
text_fixing = json.dumps(fixing, ensure_ascii=False)

# Find all 'if' conditions in VHN_fixing
conditions = re.findall(r'"condition"\s*:\s*"([^"]+)"', text_fixing)
print("Conditions:")
for c in conditions:
    print(f"  {c}")

# Find all varName + varValue pairs
def find_setvar_like(obj, results=None, path=""):
    if results is None:
        results = []
    if isinstance(obj, dict):
        if 'varName' in obj:
            results.append({
                'varName': obj.get('varName', ''),
                'varValue': obj.get('varValue', 'N/A'),
                'expression': obj.get('expression', 'N/A')[:80] if 'expression' in obj else 'N/A'
            })
        for k, v in obj.items():
            find_setvar_like(v, results, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            find_setvar_like(item, results, f"{path}[{i}]")
    return results

print("\nVHN_fixing varName/varValue:")
for sv in find_setvar_like(fixing):
    print(f"  varName={sv['varName']}, varValue={sv['varValue'][:80] if sv['varValue'] != 'N/A' else 'N/A'}")
    if sv['expression'] != 'N/A':
        print(f"    expression={sv['expression']}")

print("\n=== VHN_Optimized_Combined: varName/varValue with json.loads ===")
for sv in find_setvar_like(combined):
    val = sv.get('varValue', '')
    if val and 'json.loads' in str(val):
        print(f"  varName={sv['varName']}")
        print(f"  varValue={val[:120]}")
        print()

# Key question: does VHN_fixing use json.loads anywhere?
if 'json.loads' in text_fixing:
    print("\n!!! VHN_fixing DOES use json.loads somewhere !!!")
    # find context
    for m in re.finditer(r'json\.loads', text_fixing):
        start = max(0, m.start()-50)
        end = min(len(text_fixing), m.end()+50)
        print(f"  ...{text_fixing[start:end]}...")
else:
    print("\n>>> VHN_fixing does NOT use json.loads ANYWHERE <<<")

# Check how VHN_fixing decides product search (what triggers API call)
print("\n=== VHN_fixing: API calls ===")
def find_api_calls(obj, results=None):
    if results is None:
        results = []
    if isinstance(obj, dict):
        if obj.get('type') in ('botAPICall', 'apiCall'):
            results.append({
                'name': obj.get('name', 'unnamed'),
                'type': obj['type'],
                'url': obj.get('properties', {}).get('url', 'N/A')[:80]
            })
        for v in obj.values():
            find_api_calls(v, results)
    elif isinstance(obj, list):
        for item in obj:
            find_api_calls(item, results)
    return results

for api in find_api_calls(fixing):
    print(f"  {api['name']}: {api['type']} -> {api['url']}")

# Now check all python blocks in VHN_fixing
print("\n=== VHN_fixing: Python blocks ===")
def find_python_blocks(obj, results=None):
    if results is None:
        results = []
    if isinstance(obj, dict):
        if obj.get('type') == 'python':
            results.append({
                'name': obj.get('name', 'unnamed'),
                'varName': obj.get('properties', {}).get('varName', 'N/A'),
                'expression_len': len(obj.get('properties', {}).get('expression', '')),
                'expression_start': obj.get('properties', {}).get('expression', '')[:100]
            })
        for v in obj.values():
            find_python_blocks(v, results)
    elif isinstance(obj, list):
        for item in obj:
            find_python_blocks(item, results)
    return results

for pb in find_python_blocks(fixing):
    print(f"  {pb['name']} -> varName={pb['varName']}, len={pb['expression_len']}")
    print(f"    {pb['expression_start']}")
    print()
