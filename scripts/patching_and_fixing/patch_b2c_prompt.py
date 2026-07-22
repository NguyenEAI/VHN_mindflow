import json

with open('c:\\Users\\Administrator\\Desktop\\Hoc_python\\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def modify_node(seq):
    for node in seq:
        if node.get('name') == 'AI Chuyên trách B2C' and 'instruction' in node.get('properties', {}):
            old_inst = node['properties']['instruction']
            
            # insert exception rule right after the "Quy trình tư vấn B2C" section
            new_inst = old_inst.replace(
                '# Quy trình tư vấn B2C (linh hoạt, KHÔNG cứng nhắc nhưng phải đầy đủ các bước từ bước 1 đến bước 6, bước 7 trở đi thì linh hoạt tuỳ thuộc vào câu hỏi và trả lời của Customer)',
                '# Quy trình tư vấn B2C (linh hoạt, KHÔNG cứng nhắc)\n\n**NGOẠI LỆ TỐI CAO**: Nếu Customer yêu cầu hỏi giá hoặc thông tin của một hoặc nhiều sản phẩm cụ thể (VD: "giá của kem chống nắng này là bao nhiêu?", "cho hỏi giá Unstress 1"), ASSISTANT PHẢI TRẢ LỜI NGAY LẬP TỨC THÔNG TIN VÀ GIÁ CỦA CÁC SẢN PHẨM ĐÓ DỰA TRÊN KNOWLEDGE B2C (findproduct_data). BỎ QUA HOÀN TOÀN TỪ BƯỚC 1 ĐẾN BƯỚC 6. TUYỆT ĐỐI KHÔNG ĐƯỢC hỏi tên, loại da hay bất kỳ thông tin nào khác, HỎI GÌ TRẢ LỜI NẤY. Chỉ hỏi thông tin khai thác nhu cầu khi khách hàng chủ động yêu cầu "tư vấn sản phẩm phù hợp".\n\nCác bước tư vấn khi khách chưa biết chọn sản phẩm nào:'
            )
            node['properties']['instruction'] = new_inst
            return True
        if 'sequence' in node:
            if modify_node(node['sequence']): return True
        if 'branches' in node:
            for b in node['branches'].values():
                if modify_node(b): return True
    return False

success = modify_node(data.get('sequence', []))
if success:
    with open('c:\\Users\\Administrator\\Desktop\\Hoc_python\\VHN_DauTien_Fixed.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print('Patched AI Chuyên trách B2C successfully!')
else:
    print('AI Chuyên trách B2C Node not found!')
