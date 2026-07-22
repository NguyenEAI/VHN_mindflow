import json

file_path = r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

def fix_ai_decide(nodes):
    for n in nodes:
        if n.get('id') == 'b2c_consult_qna_decide' and n.get('type') == 'qna':
            inst = n['properties']['instruction']
            
            # Update the instruction to return 'yes' if user lists routine
            inst = inst.replace(
                'Nếu User nhắc tới tên sản phẩm, dòng sản phẩm, thương hiệu, hoặc yêu cầu đề xuất sản phẩm -> cần thông tin sản phẩm.',
                'Nếu User nhắc tới tên sản phẩm, dòng sản phẩm, thương hiệu, yêu cầu đề xuất sản phẩm, HOẶC cung cấp/liệt kê thói quen chăm sóc da hiện tại (ví dụ: đang dùng tẩy trang, rửa mặt...) -> BẮT BUỘC cần thông tin sản phẩm.'
            )
            inst = inst.replace(
                'Nếu User chỉ đang chào hỏi hoặc trả lời các thông tin khai thác nhu cầu chưa yêu cầu gợi ý -> không cần.',
                'Nếu User chỉ đang chào hỏi hoặc trả lời thông tin độ tuổi, loại da (nhưng CHƯA kể thói quen skincare) -> không cần.'
            )
            
            n['properties']['instruction'] = inst
            print("Fixed AI Decide instruction.")
            return True
            
        if 'branches' in n:
            for b in n['branches'].values():
                if fix_ai_decide(b): return True
        if 'sequence' in n:
            if fix_ai_decide(n['sequence']): return True
    return False

fix_ai_decide(data.get('sequence', []))

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Saved file.")
