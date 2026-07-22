import json

file_path = r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

def fix_nodes(nodes):
    for n in nodes:
        if n.get('id') == '52532d1c2a7a9307df8455e1d70a9c05' and n.get('type') == 'qna':
            inst = n['properties']['instruction']
            
            # The conflicting rule is:
            # "- Khi Customer hỏi về các sản phẩm homecare, điều trị tại nhà, dùng tại nhà..., Assistant mặc định chọn "vendor" là "none" và "product_type" là "none""
            # We must remove it, or change it so that it doesn't override the product_type if they are listing a routine!
            
            # Let's replace the whole FRIENDLY REMINDER section with a better one.
            old_reminder = """# FRIENDLY REMINDER
- QUAN TRỌNG: Khi Customer kể/liệt kê thói quen chăm sóc da hiện tại (ví dụ: đang dùng tẩy trang, rửa mặt, bôi chống nắng...), Assistant BẮT BUỘC phải trích xuất TẤT CẢ các product_type tương ứng với các bước đó (ví dụ: micellar, cleanser, antisun...).
- Giá trị mặc định ban đầu của "vendor" là "none"
- Giá trị mặc định ban đầu của "product_type" là "none"
- Khi Customer mentions about "peeling system", Assistant MUST chọn "vendor" là "dermoaroma" và remember to chọn "product_type" phù hợp với Customer.
- Khi Customer mentions about "line repair", Assistant MUST chọn "vendor" là "christina" và remember to chọn "product_type" phù hợp với Customer.
- Khi Customer hỏi về sản phẩm tiêm trẻ hóa da, Assistant MUST chọn "product_type" là "inject" và lựa chọn "vendor" phù hợp theo nội dung cuộc trò chuyện với Customer và gợi ý từ Sales Manager.
- Khi Customer hỏi về các sản phẩm homecare, điều trị tại nhà, dùng tại nhà..., Assistant mặc định chọn "vendor" là "none" và "product_type" là "none"
- Khi Customer hỏi thông tin về 'cicaderm' (ví dụ: cicaderm là của ai hả em) which means đang hỏi về sản phẩm `Ivatherm - Cicaderm Cream - 40ml (Kem phục hồi, hỗ trợ tái tạo da và ngăn ngừa sẹo)`, Assistant MUST chọn "product_type" là "cream" và chọn "vendor" là "ivatherm"
- Khi Customer requests more products, hỏi thêm sản phẩm, yêu cầu thêm sản phẩm..., Assistant SHOULD giữ nguyên "vendor" hoặc "product_type" đã chọn trước đó.
- Assistant REMEMBER that nước tẩy trang, dầu tẩy trang, sữa tẩy trang is the same product_type "micellar".
- Tránh nhầm lẫn khi chọn "product_type" giữa **sữa tẩy trang** và **sữa rửa mặt**.
- Khi Customer hỏi thông tin về sản phẩm "Ivatherm - Multi-Performance - Cleansing milk Face And Eyes - 200ml", Assistant SHOULD chọn "product_type" là `micellar`.
- Khi Customer hỏi về sản phẩm trị mụn lưng, Assistant SHOULD chọn vendor `christina` và product_type `exfoliate`."""

            new_reminder = """# FRIENDLY REMINDER
- TUYỆT ĐỐI QUAN TRỌNG: Khi Customer kể hoặc liệt kê thói quen chăm sóc da hiện tại (ví dụ: đang dùng tẩy trang, rửa mặt, kem chống nắng...), Assistant BẮT BUỘC phải trích xuất TẤT CẢ các product_type tương ứng với các bước đó (ví dụ: ["micellar", "cleanser", "antisun"]). Điều này ƯU TIÊN HƠN mọi quy tắc mặc định khác! KHÔNG ĐƯỢC để product_type là "none" nếu khách có kể quy trình.
- Giá trị mặc định ban đầu của "vendor" là "none"
- Giá trị mặc định ban đầu của "product_type" là "none"
- Khi Customer mentions about "peeling system", Assistant MUST chọn "vendor" là "dermoaroma" và remember to chọn "product_type" phù hợp với Customer.
- Khi Customer mentions about "line repair", Assistant MUST chọn "vendor" là "christina" và remember to chọn "product_type" phù hợp với Customer.
- Khi Customer hỏi về sản phẩm tiêm trẻ hóa da, Assistant MUST chọn "product_type" là "inject" và lựa chọn "vendor" phù hợp theo nội dung cuộc trò chuyện với Customer và gợi ý từ Sales Manager.
- CHỈ KHI Customer hỏi CHUNG CHUNG về các sản phẩm homecare, điều trị tại nhà, dùng tại nhà... MÀ KHÔNG KỂ QUY TRÌNH, Assistant mới mặc định chọn "vendor" là "none" và "product_type" là "none". Nếu có quy trình thì phải trích xuất product_type từ quy trình!
- Khi Customer hỏi thông tin về 'cicaderm', Assistant MUST chọn "product_type" là "cream" và chọn "vendor" là "ivatherm"
- Khi Customer requests more products, hỏi thêm sản phẩm, yêu cầu thêm sản phẩm..., Assistant SHOULD giữ nguyên "vendor" hoặc "product_type" đã chọn trước đó.
- Assistant REMEMBER that nước tẩy trang, dầu tẩy trang, sữa tẩy trang is the same product_type "micellar".
- Tránh nhầm lẫn khi chọn "product_type" giữa **sữa tẩy trang** và **sữa rửa mặt**.
- Khi Customer hỏi thông tin về sản phẩm "Ivatherm - Multi-Performance - Cleansing milk Face And Eyes - 200ml", Assistant SHOULD chọn "product_type" là `micellar`.
- Khi Customer hỏi về sản phẩm trị mụn lưng, Assistant SHOULD chọn vendor `christina` và product_type `exfoliate`."""
            
            if old_reminder in inst:
                inst = inst.replace(old_reminder, new_reminder)
                n['properties']['instruction'] = inst
                print("Updated GPT-4 Query Data successfully")
            else:
                print("Could not find the exact old_reminder text.")
                # Fallback: Just replace the problematic line
                bad_line = "- Khi Customer hỏi về các sản phẩm homecare, điều trị tại nhà, dùng tại nhà..., Assistant mặc định chọn \"vendor\" là \"none\" và \"product_type\" là \"none\""
                good_line = "- CHỈ KHI Customer hỏi CHUNG CHUNG về các sản phẩm homecare, điều trị tại nhà... MÀ KHÔNG KỂ QUY TRÌNH, Assistant mới chọn \"product_type\" là \"none\". Nếu có quy trình thì BẮT BUỘC phải trích xuất product_type từ quy trình (ví dụ: [\"micellar\", \"cleanser\", \"antisun\"])!"
                if bad_line in inst:
                    inst = inst.replace(bad_line, good_line)
                    n['properties']['instruction'] = inst
                    print("Updated GPT-4 Query Data using fallback replacement.")
                else:
                    print("Could not find the bad line either!")

        if 'branches' in n:
            for b_name, b_nodes in n['branches'].items():
                fix_nodes(b_nodes)
        if 'sequence' in n:
            fix_nodes(n['sequence'])

for node in data.get('sequence', []):
    if node.get('type') == 'flowSwitch':
        b2c_nodes = node.get('branches', {}).get('b2c_consult', [])
        fix_nodes(b2c_nodes)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Finished fixing JSON")
