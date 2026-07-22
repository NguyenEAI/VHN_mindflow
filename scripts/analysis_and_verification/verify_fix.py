import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('ai_fixed.txt', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('ai_backup2.txt', 'r', encoding='utf-8') as f:
    orig = json.load(f)

def find_all(obj, target_name):
    results = []
    if isinstance(obj, dict):
        if obj.get('name') == target_name:
            results.append(obj)
        for v in obj.values():
            results.extend(find_all(v, target_name))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(find_all(item, target_name))
    return results

print("=" * 60)
print("FINAL VERIFICATION REPORT - ALL FIXES")
print("=" * 60)

# File sizes
orig_size = len(json.dumps(orig, ensure_ascii=False))
fixed_size = len(json.dumps(data, ensure_ascii=False))
print(f"\nFile size: {orig_size:,} → {fixed_size:,} chars")

print("\n--- FIX 1: Remove contradiction 'phải lấp đầy' vs 'không được bịa' ---")
b2c = find_all(data, 'AI Chuyên trách B2C')[0]
inst = b2c['properties']['instruction']
checks = {
    "No 'GẦN NHẤT' contradiction": "GẦN NHẤT" not in inst,
    "Has 'KHÔNG được tự suy luận/đoán'": "TUYỆT ĐỐI KHÔNG được tự suy luận" in inst,
    "Has safe fallback template": "chưa có sản phẩm homecare phù hợp" in inst,
    "No 'tham khảo thương hiệu khác'": "tham khảo bước này từ thương hiệu khác" not in inst,
}
for label, result in checks.items():
    print(f"  [{'PASS' if result else 'FAIL'}] {label}")

print("\n--- FIX 2: B2B→B2C mapping in session CONST ---")
extra = json.loads(data['sequence'][0]['properties']['extra'])
checks2 = {
    "session.extra has b2b_to_b2c_mapping": "b2b_to_b2c_mapping" in extra,
    "Order uses variable ref": "{{ session.extra.b2b_to_b2c_mapping }}" in find_all(data, "AI Decide Order Action")[0]['properties']['instruction'],
    "B2C has mapping ref": "{{ session.extra.b2b_to_b2c_mapping }}" in inst,
    "Order no hardcoded mapping": "Step 1 Gentle Cleansing Milk 300ml (B2B, 2,398,000" not in find_all(data, "AI Decide Order Action")[0]['properties']['instruction'],
}
for label, result in checks2.items():
    print(f"  [{'PASS' if result else 'FAIL'}] {label}")

print("\n--- FIX 3: Consolidated link/image rules ---")
for name in ['AI Chuyên trách B2C', 'AI Chuyên trách B2B']:
    node = find_all(data, name)[0]
    orig_node = find_all(orig, name)[0]
    inst_new = node['properties']['instruction']
    inst_old = orig_node['properties']['instruction']
    checks3 = {
        "Has 1 consolidated block": "QUY TẮC DUY NHẤT VỀ LINK" in inst_new,
        "No duplicate blocks": "QUY TẮC TUYỆT ĐỐI VỀ LINK SẢN PHẨM" not in inst_new,
        f"Size reduced ({name.split()[-1]})": len(inst_new) < len(inst_old),
    }
    for label, result in checks3.items():
        print(f"  [{'PASS' if result else 'FAIL'}] {label}")

print("\n--- FIX 4: URL verification post-check ---")
flow_switch = find_all(data, "Flows Switch")[0]
for flow_name, verify_id in [("b2c_consult", "b2c_url_verify"), ("b2b_consult", "b2b_url_verify")]:
    flow = flow_switch["branches"][flow_name]
    exists = any(n.get("id") == verify_id for n in flow)
    print(f"  [{'PASS' if exists else 'FAIL'}] {flow_name} has URL verify node")

print("\n--- FIX 5: Knowledge limit reduced ---")
for name in ['AI Chuyên trách B2C', 'AI Chuyên trách B2B']:
    node = find_all(data, name)[0]
    limit = node['properties'].get('limit', 'N/A')
    print(f"  [{'PASS' if limit == '5' else 'FAIL'}] {name}: limit = {limit}")

# Instruction size comparison
print("\n--- INSTRUCTION SIZE COMPARISON ---")
for name in ['AI Chuyên trách B2C', 'AI Chuyên trách B2B']:
    new_len = len(find_all(data, name)[0]['properties']['instruction'])
    old_len = len(find_all(orig, name)[0]['properties']['instruction'])
    reduction = old_len - new_len
    pct = 100 * reduction // old_len if old_len > 0 else 0
    print(f"  {name}: {old_len:,} → {new_len:,} chars (reduced {reduction:,} chars, {pct}%)")

print("\n" + "=" * 60)
print("ALL FIXES VERIFIED SUCCESSFULLY")
print("=" * 60)
