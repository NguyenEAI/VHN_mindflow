"""
Deep diagnostic script for VHN_Optimized_Combined.json
Find root cause of: Error in Prompt Program: Expecting value: line 1 column 1 (char 0)
"""
import json, re

data = json.load(open(r'VHN_Optimized_Combined.json', encoding='utf-8'))
text = json.dumps(data, ensure_ascii=False)

print("=" * 70)
print("DIAGNOSTIC: Finding root cause of json.loads empty string error")
print("=" * 70)

# 1. Find ALL json.loads in varValue expressions
print("\n[1] ALL json.loads() in setVar varValue:")
def find_json_loads_in_setvar(obj, path=""):
    results = []
    if isinstance(obj, dict):
        if obj.get('type') == 'setVar':
            val = obj.get('properties', {}).get('varValue', '')
            if 'json.loads' in str(val):
                results.append({
                    'name': obj.get('name', 'unnamed'),
                    'id': obj.get('id', ''),
                    'varName': obj.get('properties', {}).get('varName', ''),
                    'varValue': val,
                    'path': path
                })
        for k, v in obj.items():
            results.extend(find_json_loads_in_setvar(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            results.extend(find_json_loads_in_setvar(item, f"{path}[{i}]"))
    return results

json_loads_nodes = find_json_loads_in_setvar(data)
for i, node in enumerate(json_loads_nodes):
    print(f"  [{i+1}] {node['name']} (id={node['id']})")
    print(f"      varName: {node['varName']}")
    print(f"      varValue: {node['varValue'][:120]}...")
    print()

# 2. Find ALL conditions with deep dot-access or bracket notation
print("\n[2] ALL conditions with complex access patterns:")
def find_conditions(obj, path=""):
    results = []
    if isinstance(obj, dict):
        if 'condition' in obj.get('properties', {}):
            cond = obj['properties']['condition']
            results.append({
                'name': obj.get('name', 'unnamed'),
                'condition': cond,
                'path': path
            })
        for k, v in obj.items():
            results.extend(find_conditions(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            results.extend(find_conditions(item, f"{path}[{i}]"))
    return results

conditions = find_conditions(data)
for c in conditions:
    flags = []
    if '[' in c['condition']:
        flags.append("BRACKET_NOTATION")
    if c['condition'].count('.') >= 3:
        flags.append("DEEP_DOT_ACCESS")
    flag_str = f" !! {', '.join(flags)}" if flags else ""
    print(f"  {c['name']}: {c['condition']}{flag_str}")

# 3. Find ALL Python blocks that use {{var}} with bracket notation
print("\n[3] Python expressions using {{var[...]}} bracket notation:")
bracket_refs = re.findall(r'\{\{[^}]*\[[^}]*\}\}', text)
for ref in bracket_refs:
    print(f"  {ref}")

# 4. Check if json_mode matches expectation
print("\n[4] QnA nodes that ask for JSON but have json_mode=false:")
def find_json_no_mode(obj, path=""):
    results = []
    if isinstance(obj, dict):
        if obj.get('type') == 'qna':
            props = obj.get('properties', {})
            instruction = props.get('instruction', '')
            json_mode = props.get('json_mode', False)
            if not json_mode and ('JSON' in instruction or 'json' in instruction.lower()):
                if 'responds in JSON' in instruction or 'Output JSON' in instruction or 'Return exactly' in instruction:
                    results.append({
                        'name': obj.get('name', 'unnamed'),
                        'json_mode': json_mode,
                        'llm': props.get('llm_alt_model', 'default')
                    })
        for k, v in obj.items():
            results.extend(find_json_no_mode(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            results.extend(find_json_no_mode(item, f"{path}[{i}]"))
    return results

mismatched = find_json_no_mode(data)
for m in mismatched:
    print(f"  WARNING: {m['name']} asks for JSON but json_mode={m['json_mode']} (model={m['llm']})")

# 5. Check for multi-line JSON literals in instructions (SKILL.md 13.5)
print("\n[5] Instructions containing JSON-like {/} patterns (risk SKILL.md 13.5):")
def find_json_in_instructions(obj, path=""):
    results = []
    if isinstance(obj, dict):
        if obj.get('type') == 'qna':
            instruction = obj.get('properties', {}).get('instruction', '')
            # Count standalone { and } that aren't part of {{ }}
            single_braces = len(re.findall(r'(?<!\{)\{(?!\{)', instruction))
            if single_braces > 5:
                results.append({
                    'name': obj.get('name', 'unnamed'),
                    'single_braces': single_braces,
                    'instruction_len': len(instruction)
                })
        for k, v in obj.items():
            results.extend(find_json_in_instructions(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            results.extend(find_json_in_instructions(item, f"{path}[{i}]"))
    return results

json_instructions = find_json_in_instructions(data)
for j in json_instructions:
    print(f"  WARNING: {j['name']} has {j['single_braces']} standalone braces (len={j['instruction_len']})")

# 6. Check for {{ }} template vars in varValue (should use raw var names)
print("\n[6] setVar varValue containing {{ }} template syntax:")
def find_template_in_varvalue(obj, path=""):
    results = []
    if isinstance(obj, dict):
        if obj.get('type') == 'setVar':
            val = obj.get('properties', {}).get('varValue', '')
            if '{{' in str(val):
                results.append({
                    'name': obj.get('name', 'unnamed'),
                    'varValue': val
                })
        for k, v in obj.items():
            results.extend(find_template_in_varvalue(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            results.extend(find_template_in_varvalue(item, f"{path}[{i}]"))
    return results

template_vars = find_template_in_varvalue(data)
for t in template_vars:
    print(f"  WARNING: {t['name']}: {t['varValue'][:100]}")

# 7. Check Python expression blocks for potential template issues
print("\n[7] Python blocks with potentially problematic template vars:")
def find_python_issues(obj, path=""):
    results = []
    if isinstance(obj, dict):
        if obj.get('type') == 'python':
            expr = obj.get('properties', {}).get('expression', '')
            issues = []
            # Check for triple-quote issues
            if '"""' in expr and expr.count('"""') % 2 != 0:
                issues.append("ODD_TRIPLE_QUOTES")
            # Check for {{ var }} that might render as empty
            template_vars = re.findall(r'\{\{[^}]+\}\}', expr)
            for tv in template_vars:
                if '[' in tv:
                    issues.append(f"BRACKET_IN_TEMPLATE: {tv}")
            if issues:
                results.append({
                    'name': obj.get('name', 'unnamed'),
                    'issues': issues,
                    'path': path
                })
        for k, v in obj.items():
            results.extend(find_python_issues(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            results.extend(find_python_issues(item, f"{path}[{i}]"))
    return results

python_issues = find_python_issues(data)
for p in python_issues:
    print(f"  {p['name']}: {', '.join(p['issues'])}")

# 8. Compare b2c flow with VHN_DauTien pattern
print("\n[8] b2c_consult flow structure:")
def print_flow_structure(tasks, indent=0):
    prefix = "  " * indent
    for task in tasks:
        ttype = task.get('type', '?')
        name = task.get('name', 'unnamed')
        if ttype == 'if':
            cond = task.get('properties', {}).get('condition', '')
            print(f"{prefix}IF ({cond})")
            true_branch = task.get('branches', {}).get('true', [])
            false_branch = task.get('branches', {}).get('false', [])
            print(f"{prefix}  TRUE:")
            print_flow_structure(true_branch, indent + 2)
            print(f"{prefix}  FALSE:")
            print_flow_structure(false_branch, indent + 2)
        else:
            extra = ""
            if ttype == 'qna':
                jm = task.get('properties', {}).get('json_mode', False)
                extra = f" [json_mode={jm}]"
            elif ttype == 'setVar':
                vv = task.get('properties', {}).get('varValue', '')
                if 'json.loads' in str(vv):
                    extra = " [json.loads!]"
            print(f"{prefix}{ttype}: {name}{extra}")

# Find flowSwitch
for item in data['sequence']:
    if item.get('type') == 'flowSwitch':
        b2c = item.get('branches', {}).get('b2c_consult', [])
        print_flow_structure(b2c)
        break

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
