"""
Fix root cause: Order prompt standalone braces + json_mode fixes
"""
import json, re

INPUT = r'c:\Users\Administrator\Desktop\Hoc_python\VHN_Optimized_Combined.json'

with open(INPUT, encoding='utf-8') as f:
    data = json.load(f)

text_full = json.dumps(data, ensure_ascii=False)

def find_node_by_id(obj, target_id):
    if isinstance(obj, dict):
        if obj.get('id') == target_id:
            return obj
        for v in obj.values():
            r = find_node_by_id(v, target_id)
            if r: return r
    elif isinstance(obj, list):
        for item in obj:
            r = find_node_by_id(item, target_id)
            if r: return r
    return None

# ============================================================
# FIX 1: Order QnA — Replace JSON examples with prose
# The {} braces in few-shot JSON examples confuse Conductify's
# template parser (SKILL.md 13.5)
# ============================================================
print("[FIX 1] Fixing Order QnA — removing standalone {} braces from few-shot examples...")

order_qna = find_node_by_id(data, 'or2_qna_decide')
instruction = order_qna['properties']['instruction']

# Count braces before fix
single_before = len(re.findall(r'(?<!\{)\{(?!\{)', instruction))
print(f"  Standalone braces before: {single_before}")

# Replace all few-shot JSON examples with prose format
# Pattern: → {...} or → Output:\n{...} 
# Replace JSON object examples with [JSON] placeholder descriptions

# Strategy: Replace the few-shot example OUTPUT sections 
# from "→ Output:\n{...}" format to prose bullet-point format

# Replace all lines that start with → { and contain JSON
# The key pattern is: → {"action":... or → Output:\n{"action":...

# Approach: Replace the "# VÍ DỤ INPUT → OUTPUT" section entirely
# with prose-based examples that don't use literal JSON

old_examples_start = "# VÍ DỤ INPUT → OUTPUT (few-shot)"
old_examples_end = "# Định dạng product_requirement"

if old_examples_start in instruction and old_examples_end in instruction:
    start_idx = instruction.index(old_examples_start)
    end_idx = instruction.index(old_examples_end)
    
    new_examples = """# VÍ DỤ INPUT → OUTPUT (few-shot)

## Ví dụ 1: User bỏ 1 SP, còn SP khác, đủ 4 field
Đơn có Kem chống nắng SPF50 (1,680,000) + Micellar Water (550,000). Tên=Nguyên, SĐT=0947010978, Địa chỉ=1/4 Võ Oanh
human_input: 'Anh không lấy kem chống nắng nữa'
→ action=CONFIRM_NEEDED, customer_name=Nguyên, customer_phone=0947010978, customer_address=1/4 Võ Oanh, product_requirement=Ivatherm - Micellar Water - 250ml (x1, 550,000 VNĐ), shipping_fee=30,000 VNĐ, total_price=580,000 VNĐ, payment_method=COD, reply_text=Dạ em đã cập nhật đơn còn Micellar Water + xác nhận.

## Ví dụ 2: User bỏ 1 SP, còn SP khác, THIẾU SĐT
Đơn có SP A + SP B. Tên=Lan, SĐT chưa có, Địa chỉ chưa có.
human_input: 'bỏ SP A đi em'
→ action=INCOMPLETE, customer_name=Lan, customer_phone=NOT-PROVIDED, customer_address=NOT-PROVIDED, product_requirement=SP B (x1, 500,000 VNĐ), shipping_fee=30,000 VNĐ, total_price=530,000 VNĐ, reply_text=Đã bỏ SP A, đơn còn SP B + hỏi SĐT và địa chỉ.

## Ví dụ 3: User 'bỏ thêm' 1 SP (bỏ thêm = xóa thêm, KHÔNG PHẢI thêm vào)
Đơn có Kem chống nắng SPF50 + Micellar Water. Tên=Nguyên, SĐT=0947010978, Địa chỉ=1/4 Võ Oanh
human_input: 'Bỏ thêm cho anh kem chống nắng nữa nha em'
Phân tích: 'Bỏ thêm' = 'additionally remove' = XÓA THÊM kem chống nắng khỏi đơn.
→ action=CONFIRM_NEEDED, loại bỏ Kem chống nắng, còn Micellar Water, xác nhận đơn.

## Ví dụ 4: User xin TƯ VẤN THÊM sản phẩm (KHÔNG PHẢI đặt hàng)
Đơn có Micellar Water (550,000). Tên=Nguyên
human_input: 'à em tư vấn cho anh thêm 1 sản phẩm toner cho da của anh đi bé'
Phân tích: User KHÔNG muốn thêm toner vào đơn. User muốn được TƯ VẤN trước. PHẢI EXIT.
→ action=EXIT, GIỮ NGUYÊN product_requirement (Micellar Water), reply_text=Dạ vâng để em tư vấn thêm, đơn vẫn được giữ nguyên.
SAI: Tự thêm 'Toner' vào product_requirement khi User chỉ xin tư vấn.
ĐÚNG: EXIT với product_requirement giữ nguyên.

## Ví dụ 5: User đổi hình thức thanh toán sang Chuyển khoản
Đơn có 3 SP tổng 2,880,000 VNĐ. Tên=Nguyên, SĐT=0947010978, Địa chỉ=1/4 Võ Oanh.
human_input: 'anh thanh toán bằng chuyển khoản nha'
→ action=CONFIRM_NEEDED, payment_method=Chuyển khoản, reply_text ghi chú nhân viên sẽ gửi thông tin CK.
SAI: Bịa số tài khoản/ngân hàng. ĐÚNG: Chỉ đổi payment_method.

## Ví dụ 6: User hủy toàn bộ
human_input: 'thôi không mua nữa em'
→ action=EXIT, product_requirement=NOT-PROVIDED.

"""
    
    instruction = instruction[:start_idx] + new_examples + instruction[end_idx:]
    print("  Replaced few-shot JSON examples with prose format")
else:
    print("  WARNING: Could not find example section markers!")

# Also replace the B2B few-shot examples section
old_b2b_start = "## VÍ DỤ FEW-SHOT (BẮT BUỘC TUÂN THEO):"
old_b2b_end = "# LƯU Ý: Nếu User là khách B2B"

if old_b2b_start in instruction and old_b2b_end in instruction:
    start_idx = instruction.index(old_b2b_start)
    end_idx = instruction.index(old_b2b_end)
    
    new_b2b_examples = """## VÍ DỤ FEW-SHOT (BẮT BUỘC TUÂN THEO):

VD A: User muốn mua Step 5 Total Serenity Serum 100ml
→ action=INCOMPLETE, product_requirement=NOT-PROVIDED, reply_text lịch sự từ chối SP B2B + gợi ý Christina Unstress Total Serenity Serum 50ml (B2C, 3,190,000 VNĐ) + hỏi xác nhận đổi.

VD B: User muốn mua Step 1 Gentle Cleansing Milk 300ml
→ action=INCOMPLETE, product_requirement=NOT-PROVIDED, reply_text giải thích B2B giá 2,398,000đ + gợi ý homecare Christina Unstress 300ml (B2C, 1,900,000đ) + hỏi đổi.

VD C: User muốn mua Step 3 Probiotic Peel để tự dùng ở nhà
→ action=INCOMPLETE, product_requirement=NOT-PROVIDED, reply_text CẢNH BÁO rủi ro peel tại nhà (bỏng rát, tổn thương da, sẹo) + khuyên đến Spa/Clinic + đề xuất SP homecare dịu nhẹ thay thế.

VD D: User muốn mua Step 6a Relaxing Massage Cream
→ action=INCOMPLETE, product_requirement=NOT-PROVIDED, reply_text giải thích 500ml dành cho Spa + gợi ý Harmonizing Night Cream 50ml (2,860,000 VNĐ).

VD E: User muốn mua Preime SKIN RENEW (ID 220)
→ action=INCOMPLETE, product_requirement=NOT-PROVIDED, reply_text giải thích SP chuyên dụng 6,600,000đ chỉ dùng tại Clinic + không bán lẻ + đề xuất homecare thay thế.

"""
    
    instruction = instruction[:start_idx] + new_b2b_examples + instruction[end_idx:]
    print("  Replaced B2B few-shot JSON examples with prose format")

# Count braces after fix
single_after = len(re.findall(r'(?<!\{)\{(?!\{)', instruction))
print(f"  Standalone braces after: {single_after}")

order_qna['properties']['instruction'] = instruction

# ============================================================
# FIX 2: Enable json_mode=true for QnA nodes that require JSON
# ============================================================
print("\n[FIX 2] Enabling json_mode=true for JSON-required QnA nodes...")

json_nodes = [
    'b2copt_ai_decide_product_search',
    'b2copt_ai_select_verified_products',
    'b2bopt_ai_decide_product_search',
    'b2bopt_ai_select_verified_products',
]

for node_id in json_nodes:
    node = find_node_by_id(data, node_id)
    if node:
        old_val = node['properties'].get('json_mode', False)
        node['properties']['json_mode'] = True
        print(f"  {node.get('name')}: json_mode {old_val} -> True")
    else:
        print(f"  WARNING: Could not find {node_id}")

# ============================================================
# Save
# ============================================================
with open(INPUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nDone! Saved to {INPUT}")
