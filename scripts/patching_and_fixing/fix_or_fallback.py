"""
ROOT CAUSE FIX: Remove all 'or' fallback from json.loads() in setVar varValue.
VHN_fixing (working) uses: json.loads(variable_name) — NO 'or' fallback.
VHN_Optimized_Combined (broken) uses: json.loads(x or '...') — WITH 'or' fallback.
Conductify's expression evaluator likely does NOT support 'or' in varValue.

FIX STRATEGY:
1. Remove 'or ...' from all json.loads() in setVar varValue
2. Ensure Python sanitizer blocks ALWAYS output valid JSON (they already do via try/except)
3. For nodes without Python sanitizer (using QnA output directly), use QnA output directly
"""
import json, re

INPUT = r'c:\Users\Administrator\Desktop\Hoc_python\VHN_Optimized_Combined.json'

with open(INPUT, encoding='utf-8') as f:
    data = json.load(f)

fix_count = 0

def fix_json_loads_or(obj, path=""):
    global fix_count
    if isinstance(obj, dict):
        if obj.get('type') == 'setVar':
            var_value = obj.get('properties', {}).get('varValue', '')
            if 'json.loads' in str(var_value) and ' or ' in str(var_value):
                # Extract the variable name from json.loads(VAR or '...')
                match = re.match(r"json\.loads\((\w+)\s+or\s+'.*'\)", var_value)
                if match:
                    var_name = match.group(1)
                    new_value = f"json.loads({var_name})"
                    obj['properties']['varValue'] = new_value
                    fix_count += 1
                    print(f"  FIX [{fix_count}] {obj.get('name', 'unnamed')} (id={obj.get('id', '')})")
                    print(f"    BEFORE: {var_value[:100]}")
                    print(f"    AFTER:  {new_value}")
                    print()
        for v in obj.values():
            fix_json_loads_or(v, f"{path}.{k}" if isinstance(v, dict) else path)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            fix_json_loads_or(item, f"{path}[{i}]")

# Fix variable name in nested iteration
def fix_json_loads_or_v2(obj):
    global fix_count
    if isinstance(obj, dict):
        if obj.get('type') == 'setVar':
            var_value = obj.get('properties', {}).get('varValue', '')
            if 'json.loads' in str(var_value) and ' or ' in str(var_value):
                match = re.match(r"json\.loads\((\w+)\s+or\s+'.*'\)", var_value)
                if match:
                    var_name = match.group(1)
                    new_value = f"json.loads({var_name})"
                    obj['properties']['varValue'] = new_value
                    fix_count += 1
                    print(f"  FIX [{fix_count}] {obj.get('name', 'unnamed')} (id={obj.get('id', '')})")
                    print(f"    BEFORE: {var_value[:100]}")
                    print(f"    AFTER:  {new_value}")
                    print()
        for k, v in obj.items():
            fix_json_loads_or_v2(v)
    elif isinstance(obj, list):
        for item in obj:
            fix_json_loads_or_v2(item)

print("=" * 60)
print("FIX: Remove 'or' fallback from json.loads() in setVar")
print("=" * 60)
print()

fix_json_loads_or_v2(data)

print(f"Total fixes: {fix_count}")

# Verify all json.loads in varValue now have NO 'or'
text = json.dumps(data, ensure_ascii=False)
remaining_or = re.findall(r'json\.loads\([^)]*\sor\s', text)
if remaining_or:
    print(f"\nWARNING: {len(remaining_or)} json.loads with 'or' still remaining!")
    for r in remaining_or:
        print(f"  {r}")
else:
    print("\nOK: No json.loads with 'or' remaining.")

# Save
with open(INPUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nSaved to {INPUT}")
