"""
FIX 3: Consolidate 6+ duplicate link/image rule blocks into 1 concise block.
Also applies to B2B instruction.
"""
import json
import sys
import re

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

# =====================================================
# The consolidated link/image rule block for B2C
# =====================================================
CONSOLIDATED_LINK_RULE_B2C = """## QUY TẮC DUY NHẤT VỀ LINK, ẢNH & CHỐNG BỊA (BẮT BUỘC)

1. LINK SẢN PHẨM:
   - CHỈ dùng URL bắt đầu bằng "http://" hoặc "https://" LẤY NGUYÊN VĂN từ Knowledge.
   - Nếu Knowledge KHÔNG có URL cho SP đó → BỎ HẲN dòng "Link sản phẩm" ra khỏi reply.
   - Thay bằng: "Anh/Chị có thể đặt mua trực tiếp qua em hoặc liên hệ hotline {{ session.extra.company_contact }} để được hỗ trợ ạ."

2. ẢNH SẢN PHẨM:
   - CHỈ dùng URL ảnh LẤY NGUYÊN VĂN từ Knowledge.
   - Nếu Knowledge KHÔNG có URL ảnh → BỎ HẲN dòng "Hình ảnh" ra khỏi reply. Mô tả bằng lời thay thế.
   - Nếu User chủ động hỏi ảnh mà Knowledge không có: "Dạ, Anh/Chị vui lòng để lại SĐT, em sẽ gửi hình ảnh chi tiết qua Zalo/SMS cho mình nhé ạ!"

3. TÊN SẢN PHẨM:
   - PHẢI ghi NGUYÊN VĂN tên SP từ Knowledge: <Thương hiệu> - <Dòng/Line> - <Tên SP> - <Dung tích>.
   - KHÔNG rút gọn, dịch lại, viết chung chung.

4. MỌI TRƯỜNG THÔNG TIN (giá, thành phần, công dụng, HDSD):
   - PHẢI lấy nguyên văn từ Knowledge.
   - Nếu thiếu trường nào → BỎ HẲN trường đó, KHÔNG ghi placeholder "[không có]", "[chưa cập nhật]", "NA".

5. CẤM TUYỆT ĐỐI:
   - KHÔNG tự tạo/đoán/bịa URL (kể cả kiểu "/san-pham/xxx", "shopee.vn/...").
   - KHÔNG dùng tên SP làm giá trị cho dòng "Link sản phẩm" hoặc "Hình ảnh".
   - KHÔNG ghép [Tên SP](link-bịa) kiểu Markdown.

VÍ DỤ SAI:
  - "Link sản phẩm: Dermoaroma - Peeling System" ← tên SP, không phải URL
  - "[Dermoaroma Peeling](https://vhn.vn/dermoaroma-peeling)" ← URL tự đoán

VÍ DỤ ĐÚNG (khi Knowledge KHÔNG có link/ảnh):
  "1. Dermoaroma - Peeling System - Restructa - 50ml
     - Giá: 9,800,000 VNĐ
     - Công dụng: Giúp thay da, giảm mụn..."
  (KHÔNG có dòng Link, KHÔNG có dòng Ảnh)

VÍ DỤ ĐÚNG (khi Knowledge CÓ link):
  "   - Link sản phẩm: https://vhndistribution.com/san-pham/kem-duong-am-..."
  (dùng nguyên văn URL từ Knowledge)"""


def fix3_consolidate_b2c(data):
    print("=" * 60)
    print("FIX 3: Consolidate link/image rules in B2C")
    print("=" * 60)
    
    nodes = find_all(data, 'AI Chuyên trách B2C')
    if not nodes:
        print("ERROR: Cannot find B2C node")
        return False
    
    inst = nodes[0]['properties']['instruction']
    original_len = len(inst)
    
    # === STEP 1: Remove duplicate blocks ===
    # We need to remove all these redundant sections and keep one consolidated block.
    
    # Blocks to remove (identified from analysis):
    blocks_to_remove = [
        # Block: "## QUY TẮC SẮT — LINK & HÌNH ẢNH PHẢI LÀ URL THẬT"
        # and its sub-sections (VÍ DỤ SAI, VÍ DỤ ĐÚNG, NGUYÊN TẮC)
        ("## QUY TẮC SẮT — LINK & HÌNH ẢNH PHẢI LÀ URL THẬT", "## Nguyên tắc 2:"),
        
        # Block: "# QUY TẮC TUYỆT ĐỐI VỀ LINK SẢN PHẨM & ẢNH"
        # and its sub-sections
        ("# QUY TẮC TUYỆT ĐỐI VỀ LINK SẢN PHẨM & ẢNH", "## 3. NGUYÊN TẮC CHUNG"),
        
        # Block: "## 3. NGUYÊN TẮC CHUNG (KHÔNG HALLUCINATE)"
        ("## 3. NGUYÊN TẮC CHUNG (KHÔNG HALLUCINATE)", "## 4. VÍ DỤ VI PHẠM"),
        
        # Block: "## 4. VÍ DỤ VI PHẠM"
        ("## 4. VÍ DỤ VI PHẠM", "# QUY TẮC ĐỊNH DẠNG OUTPUT"),
        
        # Block: "# QUY TẮC BẮT BUỘC VỀ TÊN SẢN PHẨM" - keep this BUT within our consolidated block
        
        # Block: "# QUY TẮC BẮT BUỘC VỚI LINK & ẢNH (đọc lại):"
        # This is a single-line reminder at the end
    ]
    
    # Strategy: Instead of piecemeal removal, let's identify the sections we WANT to keep,
    # and rebuild. The instruction structure is:
    # 
    # 1. Role/Tone/Xung ho
    # 2. Doi tuong
    # 3. Quy trinh tu van B2C (steps 1-6)
    # 4. QUY TAC BAT BUOC VE SO LUONG & LOAI SP (mapping rules)
    #    - Nguyen tac 1-1 MAPPING
    #    - QUY TAC SAT — KHOP 1-1 (keep)
    #    - QUY TAC SAT — LINK & HINH ANH (REMOVE - will consolidate)
    #    - Nguyen tac 2 (keep)
    #    - Nguyen tac 3 (keep)
    # 5. Buoc 8-9 (keep)
    # 6. Chinh sach van chuyen (keep)
    # 7. Quy tac dac biet voi SP B2B (keep)
    # 8. Quy tac NGHIEM NGAT (Guardrails) - has link rules mixed in
    # 9. QUY TAC TUYET DOI VE LINK (REMOVE - consolidate)
    # 10. NGUYEN TAC CHUNG (REMOVE - consolidate)
    # 11. VI DU VI PHAM (REMOVE - consolidate)
    # 12. QUY TAC DINH DANG OUTPUT (keep)
    # 13. Mau de xuat SP (keep)
    # 14. QUY TAC BAT BUOC VE TEN SP (REMOVE - move to consolidated)
    # 15. QUY TAC BAT BUOC VOI LINK & ANH (doc lai) (REMOVE)
    
    # Let's do targeted removals
    
    # REMOVAL 1: "## QUY TẮC SẮT — LINK & HÌNH ẢNH" through to before "## Nguyên tắc 2:"
    start = inst.find("## QUY TẮC SẮT — LINK & HÌNH ẢNH PHẢI LÀ URL THẬT")
    end = inst.find("## Nguyên tắc 2:")
    if start >= 0 and end >= 0:
        inst = inst[:start] + inst[end:]
        print("  [OK] Removed 'QUY TAC SAT — LINK & HINH ANH' block")
    else:
        print(f"  [WARN] Block 1 not found (start={start}, end={end})")
    
    # REMOVAL 2: "# QUY TẮC TUYỆT ĐỐI VỀ LINK SẢN PHẨM & ẢNH" through "VÍ DỤ VI PHẠM" end
    # This covers sections 9, 10, 11, 12, 13 from the analysis
    start = inst.find("# QUY TẮC TUYỆT ĐỐI VỀ LINK SẢN PHẨM & ẢNH")
    end = inst.find("# QUY TẮC ĐỊNH DẠNG OUTPUT")
    if start >= 0 and end >= 0:
        inst = inst[:start] + inst[end:]
        print("  [OK] Removed 'QUY TAC TUYET DOI VE LINK' + 'NGUYEN TAC CHUNG' + 'VI DU VI PHAM' blocks")
    else:
        print(f"  [WARN] Block 2 not found (start={start}, end={end})")
    
    # REMOVAL 3: "# QUY TẮC BẮT BUỘC VỀ TÊN SẢN PHẨM" 
    # We're moving this INTO the consolidated block
    start = inst.find("# QUY TẮC BẮT BUỘC VỀ TÊN SẢN PHẨM")
    end = inst.find("# QUY TẮC BẮT BUỘC VỚI LINK & ẢNH")
    if start >= 0 and end >= 0:
        inst = inst[:start] + inst[end:]
        print("  [OK] Removed 'QUY TAC BAT BUOC VE TEN SP' block (merged into consolidated)")
    elif start >= 0:
        # Find next section or end of text
        # The end marker might be right at the end
        remaining = inst[start:]
        next_section = remaining.find("\n# ", 1)
        if next_section >= 0:
            end = start + next_section
            inst = inst[:start] + inst[end:]
            print("  [OK] Removed 'QUY TAC BAT BUOC VE TEN SP' block (alt boundary)")
        else:
            print(f"  [WARN] Could not find end of TEN SP block")
    
    # REMOVAL 4: "# QUY TẮC BẮT BUỘC VỚI LINK & ẢNH (đọc lại):"
    start = inst.find("# QUY TẮC BẮT BUỘC VỚI LINK & ẢNH (đọc lại):")
    if start >= 0:
        # This is the very last rule, find end
        end = inst.find("\n", start + 1)
        if end < 0:
            end = len(inst)
        else:
            # Also remove the line after it (the TUYET DOI line)
            next_line_end = inst.find("\n", end + 1)
            if next_line_end >= 0:
                remaining_line = inst[end+1:next_line_end]
                if "TUYỆT ĐỐI" in remaining_line or "bịa URL" in remaining_line:
                    end = next_line_end
        inst = inst[:start].rstrip("\n") + inst[end:]
        print("  [OK] Removed 'QUY TAC BAT BUOC VOI LINK & ANH (doc lai)' block")
    
    # CLEANUP 5: Remove link/image rules duplicated inside "Quy tắc NGHIÊM NGẶT (Guardrails)"
    # These lines are mixed in with other guardrails, so we selectively remove:
    lines_to_remove = [
        "- KHÔNG bịa giá, KHÔNG bịa thông tin sản phẩm không có trong Knowledge.",
    ]
    # Actually this line is important as a guardrail - keep it. 
    # But remove the pure link-specific duplicates that appear in Guardrails
    
    # === STEP 2: Insert consolidated block ===
    # Insert before "# QUY TẮC ĐỊNH DẠNG OUTPUT"
    insert_marker = "# QUY TẮC ĐỊNH DẠNG OUTPUT"
    insert_pos = inst.find(insert_marker)
    if insert_pos >= 0:
        inst = inst[:insert_pos] + CONSOLIDATED_LINK_RULE_B2C + "\n\n" + inst[insert_pos:]
        print("  [OK] Inserted consolidated link/image rule block")
    else:
        # Insert before the Mau de xuat
        insert_marker2 = "# Mẫu đề xuất sản phẩm"
        insert_pos = inst.find(insert_marker2)
        if insert_pos >= 0:
            inst = inst[:insert_pos] + CONSOLIDATED_LINK_RULE_B2C + "\n\n" + inst[insert_pos:]
            print("  [OK] Inserted consolidated block (before Mau de xuat)")
        else:
            print("  [ERROR] Cannot find insertion point")
            return False
    
    # === STEP 3: Clean up extra newlines ===
    while "\n\n\n\n" in inst:
        inst = inst.replace("\n\n\n\n", "\n\n")
    while "\n\n\n" in inst:
        inst = inst.replace("\n\n\n", "\n\n")
    
    nodes[0]['properties']['instruction'] = inst
    
    new_len = len(inst)
    print(f"\n  Instruction size: {original_len} → {new_len} chars (reduced by {original_len - new_len} chars, {100*(original_len-new_len)//original_len}%)")
    
    return True


def fix3_consolidate_b2b(data):
    print("\n" + "=" * 60)
    print("FIX 3b: Consolidate link/image rules in B2B")
    print("=" * 60)
    
    nodes = find_all(data, 'AI Chuyên trách B2B')
    if not nodes:
        print("ERROR: Cannot find B2B node")
        return False
    
    inst = nodes[0]['properties']['instruction']
    original_len = len(inst)
    
    # B2B has similar duplicate blocks. Let's analyze and consolidate.
    
    # REMOVAL 1: "# QUY TẮC TUYỆT ĐỐI VỀ LINK SẢN PHẨM & ẢNH" + sub-blocks
    start = inst.find("# QUY TẮC TUYỆT ĐỐI VỀ LINK SẢN PHẨM & ẢNH")
    end = inst.find("# QUY TẮC ĐỊNH DẠNG OUTPUT")
    if start >= 0 and end >= 0:
        inst = inst[:start] + inst[end:]
        print("  [OK] Removed 'QUY TAC TUYET DOI' + sub-blocks in B2B")
    else:
        print(f"  [WARN] B2B block 1 not found (start={start}, end={end})")
    
    # REMOVAL 2: "# QUY TẮC BẮT BUỘC VỀ TÊN SẢN PHẨM" at the end
    start = inst.find("# QUY TẮC BẮT BUỘC VỀ TÊN SẢN PHẨM")
    if start >= 0:
        # This is at the very end of B2B instruction
        inst = inst[:start].rstrip("\n")
        print("  [OK] Removed 'QUY TAC BAT BUOC VE TEN SP' block in B2B")
    
    # Consolidated block for B2B (slightly adapted)
    CONSOLIDATED_B2B = """## QUY TẮC DUY NHẤT VỀ LINK, ẢNH & CHỐNG BỊA (BẮT BUỘC)

1. LINK SẢN PHẨM:
   - CHỈ dùng URL bắt đầu bằng "http://" hoặc "https://" LẤY NGUYÊN VĂN từ Knowledge.
   - Nếu Knowledge KHÔNG có URL → BỎ HẲN dòng "Link sản phẩm". Kết câu: "Anh/Chị liên hệ hotline {{ session.extra.company_contact }} để được hỗ trợ ạ."

2. ẢNH SẢN PHẨM:
   - CHỈ dùng URL ảnh LẤY NGUYÊN VĂN từ Knowledge.
   - Nếu Knowledge KHÔNG có URL ảnh → BỎ HẲN dòng "Hình ảnh". Mô tả bằng lời thay thế.
   - Nếu User hỏi ảnh mà Knowledge không có: "Dạ, Anh/Chị để lại SĐT, em sẽ gửi hình ảnh chi tiết qua Zalo/SMS nhé ạ!"

3. TÊN SẢN PHẨM:
   - PHẢI ghi NGUYÊN VĂN: <Thương hiệu> - <Dòng/Line> - <Tên SP> - <Dung tích>. KHÔNG rút gọn.
   - Nếu Knowledge có tên tiếng Việt mô tả, để TRONG NGOẶC ĐƠN sau tên gốc.

4. MỌI TRƯỜNG THÔNG TIN: lấy nguyên văn từ Knowledge. Thiếu → BỎ HẲN, KHÔNG dùng placeholder.

5. CẤM TUYỆT ĐỐI: KHÔNG tự tạo/đoán/bịa URL, KHÔNG dùng tên SP làm giá trị Link/Ảnh, KHÔNG ghép [Tên](link-bịa).

VÍ DỤ SAI: "Link sản phẩm: Dermoaroma - Peeling System" ← tên SP, không phải URL
VÍ DỤ ĐÚNG: "Link sản phẩm: https://vhndistribution.com/san-pham/..." (nguyên văn từ Knowledge)"""

    # Insert before "# QUY TẮC ĐỊNH DẠNG OUTPUT"
    insert_marker = "# QUY TẮC ĐỊNH DẠNG OUTPUT"
    insert_pos = inst.find(insert_marker)
    if insert_pos >= 0:
        inst = inst[:insert_pos] + CONSOLIDATED_B2B + "\n\n" + inst[insert_pos:]
        print("  [OK] Inserted consolidated block in B2B")
    else:
        # Append at end
        inst = inst.rstrip("\n") + "\n\n" + CONSOLIDATED_B2B
        print("  [OK] Appended consolidated block at end of B2B")
    
    # Clean up newlines
    while "\n\n\n" in inst:
        inst = inst.replace("\n\n\n", "\n\n")
    
    nodes[0]['properties']['instruction'] = inst
    
    new_len = len(inst)
    print(f"  B2B Instruction size: {original_len} → {new_len} chars (reduced by {original_len - new_len} chars)")
    
    return True


if __name__ == "__main__":
    data = load()
    
    ok1 = fix3_consolidate_b2c(data)
    ok2 = fix3_consolidate_b2b(data)
    
    if ok1 and ok2:
        save(data)
        print("\nFIX 3 applied and saved successfully.")
    else:
        print("\nFIX 3 had issues. Check output above.")
