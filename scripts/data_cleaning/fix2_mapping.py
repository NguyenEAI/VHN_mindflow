"""
FIX 2: Move B2B→B2C mapping table from hard-coded in 'order' flow 
to a Set CONST (session variable) available to both 'order' and 'b2c_consult'.
"""
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

INPUT_FILE = r"c:\Users\Administrator\Desktop\Hoc_python\ai_fixed.txt"

def load():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save(data):
    with open(INPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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

# The B2B→B2C mapping table (extracted from the order flow)
B2B_TO_B2C_MAPPING = """BẢNG ĐỐI CHIẾU SẢN PHẨM B2B → B2C (homecare tương đương):
- Step 1 Gentle Cleansing Milk 300ml (B2B, 2,398,000đ) → Christina Unstress Gentle Cleansing Milk 300ml homecare (B2C, ID 11, 1,900,000đ)
- Step 2 Revitalizing Toner 300ml (B2B, 2,266,000đ) → Christina Unstress Stabilizing Toner 300ml (B2C, ID 12, 1,900,000đ)
- Step 5 Total Serenity Serum 100ml (B2B, 7,150,000đ) → Christina Unstress Total Serenity Serum 50ml (B2C, ID 13, 3,190,000đ)
- Step 6a Relaxing Massage Cream 500ml (B2B) → KHÔNG có bản homecare — đề xuất Harmonizing Night Cream 50ml (ID 15) thay thế
- Step 3 Probiotic Peel 250ml (B2B) → KHÔNG có bản tự peel an toàn — cảnh báo + khuyên đến Spa/Clinic
- Preime SKIN RENEW (B2B, ID 220) → KHÔNG có bản homecare — khuyên đến Clinic"""


def fix2_move_mapping(data):
    print("=" * 60)
    print("FIX 2: Move B2B→B2C mapping to session CONST")
    print("=" * 60)
    
    # STEP 1: Add b2b_to_b2c_mapping to session.extra in Session Manager
    session_manager = data["sequence"][0]  # First node is Session Manager
    assert session_manager["name"] == "Session Manager", f"Expected Session Manager, got {session_manager['name']}"
    
    extra = json.loads(session_manager["properties"]["extra"])
    
    # Add the mapping constant
    extra["b2b_to_b2c_mapping"] = B2B_TO_B2C_MAPPING
    
    session_manager["properties"]["extra"] = json.dumps(extra, ensure_ascii=False)
    print("  [OK] Added 'b2b_to_b2c_mapping' to session.extra")
    
    # STEP 2: In the 'order' flow, replace the hard-coded mapping with reference to session variable
    order_nodes = find_all(data, "AI Decide Order Action")
    if not order_nodes:
        print("  ERROR: Cannot find 'AI Decide Order Action'")
        return False
    
    order_inst = order_nodes[0]["properties"]["instruction"]
    
    # Find the hardcoded mapping block and replace with variable reference
    old_mapping_start = "## DANH SÁCH ĐỐI CHIẾU B2B → B2C"
    old_mapping_end = "## QUY TẮC XỬ LÝ KHI USER MUỐN ĐẶT SẢN PHẨM B2B:"
    
    si = order_inst.find(old_mapping_start)
    ei = order_inst.find(old_mapping_end)
    
    if si >= 0 and ei >= 0:
        new_mapping_ref = (
            "## BẢNG ĐỐI CHIẾU B2B → B2C:\n"
            "{{ session.extra.b2b_to_b2c_mapping }}\n\n"
        )
        order_inst = order_inst[:si] + new_mapping_ref + order_inst[ei:]
        order_nodes[0]["properties"]["instruction"] = order_inst
        print("  [OK] Replaced hard-coded mapping in 'order' with {{ session.extra.b2b_to_b2c_mapping }}")
    else:
        print(f"  [WARN] Could not find mapping block boundaries. si={si}, ei={ei}")
        # Still continue - the important part is adding it to B2C
    
    # STEP 3: Add mapping reference to B2C instruction
    b2c_nodes = find_all(data, 'AI Chuyên trách B2C')
    if not b2c_nodes:
        print("  ERROR: Cannot find B2C node")
        return False
    
    b2c_inst = b2c_nodes[0]["properties"]["instruction"]
    
    # Insert before the B2B special rules section
    insert_marker = "# Quy tắc đặc biệt với SP B2B chuyên nghiệp"
    insert_pos = b2c_inst.find(insert_marker)
    
    if insert_pos >= 0:
        mapping_block = (
            "# BẢNG ĐỐI CHIẾU SẢN PHẨM B2B → B2C (khi User hỏi về SP chuyên nghiệp)\n"
            "{{ session.extra.b2b_to_b2c_mapping }}\n\n"
        )
        b2c_inst = b2c_inst[:insert_pos] + mapping_block + b2c_inst[insert_pos:]
        b2c_nodes[0]["properties"]["instruction"] = b2c_inst
        print("  [OK] Added mapping reference to B2C instruction")
    else:
        print("  [WARN] Could not find insert point in B2C")
    
    return True


if __name__ == "__main__":
    data = load()
    ok = fix2_move_mapping(data)
    if ok:
        save(data)
        print("\nFIX 2 applied and saved successfully.")
    else:
        print("\nFIX 2 had issues.")
