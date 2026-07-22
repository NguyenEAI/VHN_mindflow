"""
Fix script for VHN_Optimized_Combined.json
Applies all approved fixes from the implementation plan.
"""
import json, copy, sys

INPUT_FILE = r'c:\Users\Administrator\Desktop\Hoc_python\VHN_Optimized_Combined.json'
OUTPUT_FILE = r'c:\Users\Administrator\Desktop\Hoc_python\VHN_Optimized_Combined.json'
BACKUP_FILE = r'c:\Users\Administrator\Desktop\Hoc_python\VHN_Optimized_Combined_BACKUP.json'

with open(INPUT_FILE, encoding='utf-8') as f:
    data = json.load(f)

# Save backup
with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"[BACKUP] Saved to {BACKUP_FILE}")

# Helper: find node by ID recursively
def find_node_by_id(obj, target_id):
    if isinstance(obj, dict):
        if obj.get('id') == target_id:
            return obj
        for v in obj.values():
            result = find_node_by_id(v, target_id)
            if result:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = find_node_by_id(item, target_id)
            if result:
                return result
    return None

# Helper: remove nodes by ID from all lists
def remove_nodes_by_ids(obj, ids_to_remove):
    if isinstance(obj, dict):
        for key, value in list(obj.items()):
            if isinstance(value, list):
                obj[key] = [item for item in value 
                           if not (isinstance(item, dict) and item.get('id') in ids_to_remove)]
                for item in obj[key]:
                    remove_nodes_by_ids(item, ids_to_remove)
            else:
                remove_nodes_by_ids(value, ids_to_remove)
    elif isinstance(obj, list):
        for item in obj:
            remove_nodes_by_ids(item, ids_to_remove)

seq = data['sequence']

# ============================================================
# BUG #1: Move flowSwitch + filters into Safety Net false branch
# ============================================================
print("\n[BUG #1] Moving flowSwitch + botReplyFilters into Safety Net false branch...")

safety_net = seq[2]   # if (Safety Net)
flow_switch = seq[3]  # flowSwitch
filters = seq[4:]     # 5 botReplyFilters

# Verify
assert safety_net['type'] == 'if', f"Expected 'if', got '{safety_net['type']}'"
assert flow_switch['type'] == 'flowSwitch', f"Expected 'flowSwitch', got '{flow_switch['type']}'"
assert len(filters) == 5, f"Expected 5 filters, got {len(filters)}"
assert all(f['type'] == 'botReplyFilter' for f in filters), "Not all are botReplyFilter"

# Move into false branch
safety_net['branches']['false'] = [flow_switch] + filters

# Keep only session, router, safety_net in top-level
data['sequence'] = seq[:3]

print("  ✓ Moved flowSwitch + 5 botReplyFilters into false branch")
print(f"  ✓ Top-level sequence now has {len(data['sequence'])} items: "
      f"{[s.get('type') for s in data['sequence']]}")

# ============================================================
# BUG #4: Order max_tokens 500 → 800
# ============================================================
print("\n[BUG #4] Fixing Order QnA max_tokens...")

order_qna = find_node_by_id(data, 'or2_qna_decide')
assert order_qna is not None, "Could not find or2_qna_decide"
old_val = order_qna['properties']['max_tokens']
order_qna['properties']['max_tokens'] = '800'
print(f"  ✓ max_tokens: {old_val} → 800")

# ============================================================
# BUG #5: Enable human_input_aware for Gather Requirement nodes
# ============================================================
print("\n[BUG #5] Enabling human_input_aware for Gather Requirement nodes...")

for node_id, label in [
    ('b2copt_ai_gather_requirement_no_product', 'B2C'),
    ('b2bopt_ai_gather_requirement_no_product', 'B2B')
]:
    node = find_node_by_id(data, node_id)
    assert node is not None, f"Could not find {node_id}"
    node['properties']['chat_history_aware'] = True
    node['properties']['human_input_aware'] = True
    print(f"  ✓ {label} Gather Requirement: chat_history_aware=True, human_input_aware=True")

# ============================================================
# Parse session extra for modifications
# ============================================================
extra_str = data['sequence'][0]['properties']['extra']
extra = json.loads(extra_str)

# ============================================================
# WARN #3: Hardcode b2b_to_b2c_mapping into Order prompt
# ============================================================
print("\n[WARN #3] Hardcoding b2b_to_b2c_mapping into Order prompt...")

b2b_mapping = extra.get('b2b_to_b2c_mapping', '')
assert b2b_mapping, "b2b_to_b2c_mapping not found in session extra"

# Replace template var in Order QnA instruction
instruction = order_qna['properties']['instruction']
assert '{{ session.extra.b2b_to_b2c_mapping }}' in instruction, \
    "Template var not found in Order instruction"
instruction = instruction.replace('{{ session.extra.b2b_to_b2c_mapping }}', b2b_mapping)
order_qna['properties']['instruction'] = instruction

# Remove from session extra
del extra['b2b_to_b2c_mapping']
print(f"  ✓ Replaced template var with actual mapping ({len(b2b_mapping)} chars)")
print("  ✓ Removed b2b_to_b2c_mapping from session extra")

# ============================================================
# WARN #4: Remove unused session vars
# ============================================================
print("\n[WARN #4] Removing unused session vars...")

for var in ['cart', 'consultation_stage', 'employee_id', 'employee_dept']:
    if var in extra:
        del extra[var]
        print(f"  ✓ Removed '{var}' from session extra")

# ============================================================
# IMP #4: Remove findproduct_chat_history (zombie var)
# ============================================================
print("\n[IMP #4] Removing findproduct_chat_history...")

if 'findproduct_chat_history' in extra:
    del extra['findproduct_chat_history']
    print("  ✓ Removed 'findproduct_chat_history' from session extra")

# Remove the clear setVar blocks
ids_to_remove = {'or_exit_clear_findproduct_hist', 'or_done_clear_findproduct_hist'}
remove_nodes_by_ids(data, ids_to_remove)
print(f"  ✓ Removed {len(ids_to_remove)} setVar clear blocks for findproduct_chat_history")

# Save session extra back
data['sequence'][0]['properties']['extra'] = json.dumps(extra, ensure_ascii=False)

# ============================================================
# IMP #1: Add shipping info to B2C Reply prompt
# ============================================================
print("\n[IMP #1] Adding shipping info to B2C Reply prompt...")

b2c_reply = find_node_by_id(data, 'b2copt_ai_reply_from_verified_products')
assert b2c_reply is not None, "Could not find b2copt_ai_reply_from_verified_products"

instruction = b2c_reply['properties']['instruction']
shipping_block = (
    "\n# Chính sách vận chuyển & thanh toán (cung cấp khi User hỏi)\n"
    "- Đơn hàng từ 1,000,000 VNĐ trở lên: MIỄN PHÍ vận chuyển.\n"
    "- Đơn dưới 1,000,000 VNĐ: phí ship 30,000 VNĐ. Áp dụng toàn quốc.\n"
    "- Thanh toán: COD (thanh toán khi nhận hàng) hoặc Chuyển khoản ngân hàng.\n\n"
)
instruction = instruction.replace('Hard rules:', shipping_block + 'Hard rules:')
b2c_reply['properties']['instruction'] = instruction
print("  ✓ Added shipping & payment policy to B2C Reply instruction")

# ============================================================
# IMP #2 + #3: Add guardrails to B2C Reply
# ============================================================
print("\n[IMP #2+#3] Adding guardrails to B2C/B2B Reply prompts...")

# B2C: add is_salon_product guard + financial info guard
instruction = b2c_reply['properties']['instruction']
b2c_extra_rules = (
    "- ONLY recommend homecare products (is_salon_product=False). Do NOT recommend professional/salon products.\n"
    "- TUYỆT ĐỐI KHÔNG BỊA thông tin tài chính (số tài khoản ngân hàng, tên ngân hàng, mã QR, link thanh toán). "
    "Nếu User hỏi → hướng dẫn liên hệ hotline.\n"
)
instruction = instruction.replace('- Keep concise', b2c_extra_rules + '- Keep concise')
b2c_reply['properties']['instruction'] = instruction
print("  ✓ B2C Reply: added is_salon_product guard + no-fake-financial-info")

# B2B: add financial info guard
b2b_reply = find_node_by_id(data, 'b2bopt_ai_reply_from_verified_products')
assert b2b_reply is not None, "Could not find b2bopt_ai_reply_from_verified_products"

instruction = b2b_reply['properties']['instruction']
b2b_extra_rules = (
    "- TUYỆT ĐỐI KHÔNG BỊA thông tin tài chính (số tài khoản ngân hàng, tên ngân hàng, mã QR, link thanh toán). "
    "Nếu User hỏi → hướng dẫn liên hệ hotline.\n"
)
instruction = instruction.replace('- Keep concise', b2b_extra_rules + '- Keep concise')
b2b_reply['properties']['instruction'] = instruction
print("  ✓ B2B Reply: added no-fake-financial-info")

# ============================================================
# Save output
# ============================================================
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n{'='*60}")
print(f"[DONE] All fixes applied! Output: {OUTPUT_FILE}")
print(f"[BACKUP] Original saved to: {BACKUP_FILE}")
print(f"{'='*60}")
