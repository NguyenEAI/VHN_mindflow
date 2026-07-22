import json

file_path = r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

def update_nodes(nodes):
    for n in nodes:
        # 1. Update GPT-4 Query Data
        if n.get('id') == '52532d1c2a7a9307df8455e1d70a9c05' and n.get('type') == 'qna':
            inst = n['properties']['instruction']
            # We want to add a rule about extracting from customer's routine.
            new_rule = "\n- QUAN TRỌNG: Khi Customer kể/liệt kê thói quen chăm sóc da hiện tại (ví dụ: đang dùng tẩy trang, rửa mặt, bôi chống nắng...), Assistant BẮT BUỘC phải trích xuất TẤT CẢ các product_type tương ứng với các bước đó (ví dụ: micellar, cleanser, antisun...).\n"
            if "QUAN TRỌNG: Khi Customer kể" not in inst:
                inst = inst.replace("# FRIENDLY REMINDER", "# FRIENDLY REMINDER" + new_rule)
                n['properties']['instruction'] = inst
                print("Updated GPT-4 Query Data")

        # 2. Update Python product_wishlist
        if n.get('id') == '587546d6bed1f80d58351331a8bc7e79' and n.get('type') == 'python':
            expr = n['properties']['expression']
            old_loop = """for product in PRODUCTS:
    title = product.get('name', '').replace("\\n", "").strip()
    content += f"- {title}\\n\"\"\""""
            
            # Since exact match of old_loop might fail due to whitespace, let's just replace the whole expression
            new_expr = """PRODUCTS = {{api_raw_product_data[0].data}}

# Tạo nội dung rút gọn TỐI ĐA (Chỉ lấy Tên SP và Keywords) cho LLM Analysis để tiết kiệm token
content = ""
for product in PRODUCTS:
    title = product.get('name', '').replace("\\n", "").strip()
    keywords = product.get('keywords', '').replace("\\n", "").strip()
    content += f"- {title} (Phù hợp: {keywords})\\n"
    
print(content)"""
            n['properties']['expression'] = new_expr
            print("Updated Python product_wishlist")

        # 3. Update GPT-4 Analysis
        if n.get('id') == '6d3f02d97dab85e491a60d076f675a58' and n.get('type') == 'qna':
            inst = n['properties']['instruction']
            new_rule = "\n- ĐẶC BIỆT: Khi Customer có liệt kê thói quen skincare các bước, Assistant BẮT BUỘC phải chọn ra ÍT NHẤT MỘT sản phẩm cho MỖI BƯỚC trong thói quen đó (ví dụ: phải có đủ tẩy trang, sữa rửa mặt, kem chống nắng...) nếu Product List có. Chọn tất cả các sản phẩm phù hợp với tình trạng da, KHÔNG giới hạn số lượng.\n"
            if "ĐẶC BIỆT: Khi Customer có liệt kê" not in inst:
                inst = inst.replace("# FRIENDLY REMINDER", "# FRIENDLY REMINDER" + new_rule)
                n['properties']['instruction'] = inst
                print("Updated GPT-4 Analysis")

        if 'branches' in n:
            for b_name, b_nodes in n['branches'].items():
                update_nodes(b_nodes)
        if 'sequence' in n:
            update_nodes(n['sequence'])

for node in data.get('sequence', []):
    if node.get('type') == 'flowSwitch':
        b2c_nodes = node.get('branches', {}).get('b2c_consult', [])
        update_nodes(b2c_nodes)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Finished updating JSON")
