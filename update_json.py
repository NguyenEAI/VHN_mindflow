import json
import os

file_path = r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find the node
target_b = None
for node in data.get('sequence', []):
    if node.get('type') == 'flowSwitch':
        for b in node.get('branches', {}).get('b2c_consult', []):
            if b.get('type') == 'qna' and b.get('id') == '8a045fd50c088e3adf5f000f40c21d66':
                target_b = b
                break

if target_b:
    instruction = target_b['properties']['instruction']
    
    # We will replace the "Nguyên tắc 1-1 MAPPING..." text and "Nguyên tắc 2..." text with updated rules.
    # To do this safely, we will do targeted string replacements.
    
    old_text_1 = """## Nguyên tắc 1-1 MAPPING với thói quen skincare khách kể:
Khi Customer LIỆT KÊ thói quen skincare (VD: "tẩy trang, rửa mặt, bôi serum, kem chống nắng") → BẮT BUỘC đề xuất ĐỦ TẤT CẢ các bước mà khách đã kể, KHÔNG ĐƯỢC BỎ SÓT bước nào.

### VÍ DỤ MAPPING BẮT BUỘC:
Customer: "Anh tẩy trang, rửa mặt và bôi serum mỗi tối. Sáng thì bôi thêm kem chống nắng trước khi ra đường"
→ Phân tích các bước khách kể: (1) Tẩy trang, (2) Rửa mặt, (3) Serum, (4) Kem chống nắng → 4 bước
→ BẮT BUỘC đề xuất ĐỦ 4 SẢN PHẨM tương ứng 4 bước:
  1. SP TẨY TRANG (Cleansing Water / Micellar Water / Makeup Remover) — phù hợp da khách
  2. SP SỮA RỬA MẶT (Cleansing Gel / Foam) — phù hợp da khách
  3. SP SERUM — phù hợp tình trạng da cụ thể của khách (nếu khách bị nám → serum trị nám/làm sáng; nếu khách bị mụn → serum trị mụn)
  4. SP KEM CHỐNG NẮNG — phù hợp da khách
→ SAI: chỉ đề xuất 2 SP (Sữa rửa mặt + Kem chống nắng) — THIẾU tẩy trang và serum."""

    new_text_1 = """## Nguyên tắc 1-1 MAPPING với thói quen skincare khách kể VÀ Tình trạng da:
Khi Customer LIỆT KÊ thói quen skincare (VD: "tẩy trang, rửa mặt, bôi serum, kem chống nắng") và CUNG CẤP tình trạng da (VD: "da dầu mụn"):
1. BẮT BUỘC đề xuất ĐỦ TẤT CẢ các bước mà khách đã kể, KHÔNG ĐƯỢC BỎ SÓT bước nào.
2. Các sản phẩm được đề xuất tương ứng với mỗi bước PHẢI có tác dụng ĐÚNG với tình trạng da của khách.
   VD: Khách da dầu mụn, đang dùng rửa mặt và tẩy trang → Đề xuất Sữa rửa mặt cho da dầu mụn VÀ Tẩy trang cho da dầu mụn.
   - Nếu không có SP đáp ứng cả "dầu" và "mụn" → Đề xuất SP cho "da dầu" HOẶC "da mụn".
3. CHỈ SAU KHI đã đề xuất ĐẦY ĐỦ các sản phẩm tương ứng với thói quen hiện tại của khách, Assistant MỚI ĐƯỢC PHÉP đề xuất thêm các sản phẩm bổ sung (ví dụ: tẩy da chết, serum trị mụn) để tăng hiệu quả. TUYỆT ĐỐI KHÔNG đề xuất sản phẩm bổ sung thay thế cho các bước khách đang dùng hoặc khi chưa hoàn thành việc tư vấn theo quy trình của khách.

### VÍ DỤ MAPPING BẮT BUỘC:
Customer: "Da anh dầu mụn, anh tẩy trang, rửa mặt và bôi kem chống nắng"
→ Phân tích các bước khách kể: (1) Tẩy trang, (2) Rửa mặt, (3) Kem chống nắng. Tình trạng da: Dầu mụn.
→ BẮT BUỘC đề xuất ĐỦ 3 SẢN PHẨM tương ứng TRƯỚC:
  1. SP TẨY TRANG — phù hợp da dầu mụn (nếu không có thì da dầu hoặc da mụn)
  2. SP SỮA RỬA MẶT — phù hợp da dầu mụn
  3. SP KEM CHỐNG NẮNG — phù hợp da dầu mụn
→ Sau khi đề xuất xong 3 sản phẩm trên, Assistant có thể nói thêm: "Để kiểm soát dầu và giảm mụn tốt hơn, anh có thể bổ sung thêm Tẩy tế bào chết 1-2 lần/tuần..." rồi đề xuất thêm SP Tẩy da chết.
→ SAI: Chỉ đề xuất Tẩy da chết và bỏ qua Tẩy trang, Rửa mặt, Kem chống nắng."""

    if old_text_1 in instruction:
        instruction = instruction.replace(old_text_1, new_text_1)
        print("Text 1 replaced successfully.")
    else:
        print("Text 1 NOT FOUND.")
        
    target_b['properties']['instruction'] = instruction
    
    # Save back
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("JSON updated successfully.")
else:
    print("Target node not found.")
