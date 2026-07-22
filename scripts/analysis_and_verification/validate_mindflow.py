import json, re

data = json.load(open(r'c:\Users\Administrator\Desktop\Hoc_python\VHN_Optimized_Combined.json', encoding='utf-8'))
text = json.dumps(data)

# Helper: find all nodes of a type recursively
def find_all_by_type(obj, target_type):
    results = []
    if isinstance(obj, dict):
        if obj.get('type') == target_type:
            results.append(obj)
        for v in obj.values():
            results.extend(find_all_by_type(v, target_type))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(find_all_by_type(item, target_type))
    return results

# 1. Count flowSwitch (should be exactly 1 total, now inside Safety Net false branch)
all_fs = find_all_by_type(data, 'flowSwitch')
# Check it's inside Safety Net false branch, not top-level
top_level_fs = sum(1 for b in data.get('sequence', []) if b.get('type') == 'flowSwitch')
print(f'[1] flowSwitch total: {len(all_fs)} {"OK" if len(all_fs) == 1 else "SAI!"}')
print(f'    Top-level: {top_level_fs} (should be 0 after BUG#1 fix)')
safety_net = data['sequence'][2] if len(data['sequence']) > 2 else None
if safety_net and safety_net.get('type') == 'if':
    false_fs = sum(1 for b in safety_net.get('branches', {}).get('false', []) if b.get('type') == 'flowSwitch')
    print(f'    Inside Safety Net false: {false_fs} {"OK" if false_fs == 1 else "SAI!"}')

# 2. Complex conditions
complex_conds = re.findall(r'"condition":\s*"[^"]*(?:!=|\sand\s|\()[^"]*"', text)
print(f'[2] Complex conditions: {len(complex_conds)} {"OK" if len(complex_conds) == 0 else "SAI!"}')

# 3. {{var}} in conditions
templated_conds = re.findall(r'"condition":\s*"[^"]*\{\{[^"]*"', text)
print(f'[3] Templated conditions: {len(templated_conds)} {"OK" if len(templated_conds) == 0 else "SAI!"}')

# 4. setTopic component
set_topics = re.findall(r'"type":\s*"setTopic"', text)
print(f'[4] setTopic components: {len(set_topics)} {"OK" if len(set_topics) == 0 else "SAI!"}')

# 5. parallel components
parallels = re.findall(r'"type":\s*"parallel"', text)
print(f'[5] parallel components: {len(parallels)} {"OK" if len(parallels) == 0 else "CHECK!"}')

# 6. recall with non-empty properties
recall_with_props = re.findall(r'"type":\s*"recall"[^}]*"properties":\s*\{[^}]+\}', text)
print(f'[6] recall with non-empty properties: {len(recall_with_props)} {"OK" if len(recall_with_props) == 0 else "SAI!"}')

# 7. {{#if}} in botSendText text
botsend_if = re.findall(r'"type":\s*"botSendText".*?"text":\s*"[^"]*\{\{#if[^"]*"', text)
print(f'[7] botSendText with #if: {len(botsend_if)} {"OK" if len(botsend_if) == 0 else "SAI!"}')

# 8. Count nested if depth per branch
def count_if_depth(obj, depth=0):
    max_depth = depth
    if isinstance(obj, dict):
        if obj.get('type') == 'if':
            depth += 1
            max_depth = depth
        for v in obj.values():
            d = count_if_depth(v, depth)
            max_depth = max(max_depth, d)
    elif isinstance(obj, list):
        for item in obj:
            d = count_if_depth(item, depth)
            max_depth = max(max_depth, d)
    return max_depth

if all_fs:
    fs = all_fs[0]
    for topic, branch in fs.get('branches', {}).items():
        depth = count_if_depth(branch)
        status = 'OK' if depth <= 3 else 'WARNING >3!'
        print(f'[8] Branch "{topic}": if depth = {depth} {status}')

# 9. Safety net
for s in find_all_by_type(data, 'if'):
    if 'recall_counter' in s.get('properties', {}).get('condition', ''):
        cond = s['properties']['condition']
        print(f'[9] Safety Net condition: "{cond}"')

# 10. Topics
if all_fs:
    fs = all_fs[0]
    topics = list(fs.get('branches', {}).keys())
    conditions = fs.get('properties', {}).get('conditions', {})
    print(f'[10] Topics ({len(topics)}): {topics}')

# 11. Empty false + sibling
def check_empty_false_siblings(obj, path=""):
    issues = []
    if isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, dict) and item.get('type') == 'if':
                branches = item.get('branches', {})
                false_branch = branches.get('false', [])
                if false_branch == [] and i < len(obj) - 1:
                    issues.append(f'{path}[{i}] - if with empty false followed by sibling task')
            issues.extend(check_empty_false_siblings(item, f'{path}[{i}]'))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            issues.extend(check_empty_false_siblings(v, f'{path}.{k}'))
    return issues

issues = check_empty_false_siblings(data)
print(f'[11] Empty false + sibling: {len(issues)} {"OK" if not issues else "WARNING!"}')
for issue in issues:
    print(f'  -> {issue}')

# 12. Duplicate IDs
all_ids = re.findall(r'"id":\s*"([^"]+)"', text)
seen = set()
dupes = set()
for id_val in all_ids:
    if id_val in seen:
        dupes.add(id_val)
    seen.add(id_val)
print(f'[12] Duplicate IDs: {len(dupes)} {"OK" if not dupes else "WARNING!"}')
for d in dupes:
    print(f'  -> {d}')

# 13. Session extra vars
extra_str = data['sequence'][0]['properties']['extra']
extra = json.loads(extra_str)
expected_vars = ['customer_type', 'customer_name', 'customer_phone', 'customer_address',
                 'chat_history_b2b', 'chat_history_b2c', 'registration_chat_history',
                 'findproduct_data', 'old_order_customer_information',
                 'assistant_role', 'assistant_tone', 'vn_pronoun',
                 'company_name', 'company_short_name', 'company_contact',
                 'shipping_policy', 'shipping_fee_threshold', 'shipping_fee_amount']
missing = [v for v in expected_vars if v not in extra]
print(f'[13] Session extra missing vars: {len(missing)} {"OK" if not missing else "WARNING!"}')
for m in missing:
    print(f'  -> {m}')

# 14. Removed vars check (should NOT exist)
removed_vars = ['cart', 'consultation_stage', 'employee_id', 'employee_dept', 
                'findproduct_chat_history', 'b2b_to_b2c_mapping']
still_present = [v for v in removed_vars if v in extra]
print(f'[14] Removed vars still in session: {len(still_present)} {"OK" if not still_present else "SAI!"}')
for v in still_present:
    print(f'  -> {v} still present!')

# 15. Top-level structure check
print(f'\n[15] Top-level structure:')
for i, s in enumerate(data['sequence']):
    stype = s.get('type', 'unknown')
    sname = s.get('name', 'unnamed')
    if stype == 'if':
        false_count = len(s.get('branches', {}).get('false', []))
        true_count = len(s.get('branches', {}).get('true', []))
        print(f'  [{i}] {stype}: {sname} (true={true_count} tasks, false={false_count} tasks)')
    else:
        print(f'  [{i}] {stype}: {sname}')

# 16. Verify BUG #5 fix
for node_id, label in [('b2copt_ai_gather_requirement_no_product', 'B2C'),
                         ('b2bopt_ai_gather_requirement_no_product', 'B2B')]:
    def find_by_id(obj, tid):
        if isinstance(obj, dict):
            if obj.get('id') == tid: return obj
            for v in obj.values():
                r = find_by_id(v, tid)
                if r: return r
        elif isinstance(obj, list):
            for item in obj:
                r = find_by_id(item, tid)
                if r: return r
        return None
    node = find_by_id(data, node_id)
    if node:
        hi = node['properties'].get('human_input_aware')
        ch = node['properties'].get('chat_history_aware')
        ok = hi == True and ch == True
        print(f'[16] {label} Gather Req: human_input={hi}, chat_history={ch} {"OK" if ok else "SAI!"}')

print("\n=== VALIDATION COMPLETE ===")
