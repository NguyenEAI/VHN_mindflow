"""
Script to fix errors in ai_fixed.txt step by step.
Each fix is applied independently and verified before moving on.
"""
import json
import sys
import os

os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8')

INPUT_FILE = r"c:\Users\Administrator\Desktop\Hoc_python\ai_fixed.txt"
OUTPUT_FILE = INPUT_FILE  # overwrite in place

def load():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save(data):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_node_by_name(sequence, name):
    """Recursively find a node by name in the flow tree."""
    for node in sequence:
        if node.get("name") == name:
            return node
        branches = node.get("branches", {})
        if isinstance(branches, dict):
            for bname, bnodes in branches.items():
                if isinstance(bnodes, list):
                    result = find_node_by_name(bnodes, name)
                    if result:
                        return result
    return None

def get_flow_switch(data):
    """Get the Flows Switch node."""
    return find_node_by_name(data["sequence"], "Flows Switch")

def get_flow_nodes(data, flow_name):
    """Get nodes in a specific flow."""
    fs = get_flow_switch(data)
    return fs["branches"].get(flow_name, [])

# ============================================================
# FIX 1: Remove contradiction in B2C instruction
# ============================================================
def fix1_remove_contradiction(data):
    print("=" * 60)
    print("FIX 1: Remove contradiction in B2C instruction")
    print("=" * 60)
    
    b2c_nodes = get_flow_nodes(data, "b2c_consult")
    b2c_ai = find_node_by_name(b2c_nodes, "AI Chuyên trách B2C")
    if not b2c_ai:
        print("ERROR: Cannot find 'AI Chuyen trach B2C'")
        return False
    
    instruction = b2c_ai["properties"]["instruction"]
    
    # Debug: check what format the text is in
    key_phrase = "GẦN NHẤT"
    if key_phrase in instruction:
        print(f"  Found key phrase '{key_phrase}' in instruction")
    else:
        print(f"  Key phrase '{key_phrase}' NOT found in instruction")
        # Show a snippet around the area
        idx = instruction.find("THIẾU SP")
        if idx >= 0:
            print(f"  Found 'THIEU SP' at position {idx}")
            snippet = instruction[max(0,idx-50):idx+200]
            print(f"  Context: ...{repr(snippet)}...")
        else:
            print("  'THIEU SP' not found either")
            # Try searching for English keywords
            for kw in ["KNOWLEDGE", "knowledge", "Knowledge", "homecare", "sản phẩm"]:
                count = instruction.count(kw)
                print(f"  Count of '{kw}': {count}")
        return False
    
    # ---- Part A: Replace the contradictory block ----
    # The old text: "NẾU KNOWLEDGE THIẾU SP CHO 1 BƯỚC NÀO ĐÓ:" block
    # that says "Vẫn PHẢI tìm sản phẩm GẦN NHẤT"
    
    # Find boundaries
    start_marker = "NẾU KNOWLEDGE THIẾU SP CHO 1 BƯỚC NÀO ĐÓ:"
    si = instruction.find(start_marker)
    
    # Find the end: the next section starts with "## Quy tắc" or "\n\n## " or similar
    # Look for the next "##" or "\\n\\n##" after the start
    end_phrase = "→ KHÔNG được dùng câu chung chung"
    ei = instruction.find(end_phrase, si)
    
    if si < 0 or ei < 0:
        print(f"  Could not find boundaries. si={si}, ei={ei}")
        return False
    
    # Find the end of the line containing end_phrase
    # In the JSON string, newlines are represented as \n (literal characters in the parsed string)
    eol = instruction.find("\n", ei)
    if eol < 0:
        eol = len(instruction)
    
    old_block = instruction[si:eol]
    print(f"  Found old block (len={len(old_block)}):")
    print(f"  Preview: {old_block[:120]}...")
    
    new_block = (
        "NẾU KNOWLEDGE THIẾU SP CHO 1 BƯỚC NÀO ĐÓ:\n"
        "PHẢI ghi rõ ràng:\n"
        "  \"Bước [X] - [Loại SP]: Hiện tại Y dược VHN chưa có sản phẩm homecare phù hợp cho bước này. "
        "Anh/Chị vui lòng liên hệ {{ session.extra.company_contact }} để được tư vấn thêm ạ.\"\n"
        "TUYỆT ĐỐI KHÔNG được tự suy luận/đoán ra sản phẩm thay thế nếu Knowledge không có.\n"
        "TUYỆT ĐỐI KHÔNG được dùng câu chung chung kiểu \"em khuyên anh chọn sản phẩm cấp ẩm nhẹ nhàng\" — đây là né tránh, không phải đề xuất."
    )
    
    instruction = instruction[:si] + new_block + instruction[eol:]
    print("  [OK] Replaced contradictory block")
    
    # ---- Part B: Fix Nguyen tac 3 ----
    old_nt3 = "anh/chị có thể tham khảo bước này từ thương hiệu khác hoặc liên hệ"
    if old_nt3 in instruction:
        new_nt3 = "Anh/Chị vui lòng liên hệ"
        instruction = instruction.replace(old_nt3, new_nt3)
        print("  [OK] Fixed Nguyen tac 3 - removed 'tham khao thuong hieu khac'")
    else:
        print("  [INFO] Nguyen tac 3 text not found (may be different wording)")
    
    b2c_ai["properties"]["instruction"] = instruction
    
    # Verify
    assert "Vẫn PHẢI tìm sản phẩm GẦN NHẤT" not in instruction, "Contradiction still exists!"
    print("  [VERIFY] No contradiction text remains")
    
    return True


if __name__ == "__main__":
    step = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    
    data = load()
    
    if step == 1:
        ok = fix1_remove_contradiction(data)
        if ok:
            save(data)
            print("\nFIX 1 applied and saved successfully.")
        else:
            print("\nFIX 1 failed. File not modified.")
            sys.exit(1)
