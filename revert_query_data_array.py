import json

file_path = r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

def update_to_array(nodes):
    for n in nodes:
        if n.get('id') == '52532d1c2a7a9307df8455e1d70a9c05' and n.get('type') == 'qna':
            inst = n['properties']['instruction']
            
            # Revert to array instruction
            inst = inst.replace(
                '* "product_type": MỘT CHUỖI DUY NHẤT (string), KHÔNG PHẢI ARRAY. Nếu có nhiều loại, hãy ngăn cách bằng dấu phẩy (ví dụ: "product_type": "serum, cleanser, antisun")',
                '* "product_type": có thể là 1 giá trị, hoặc là array các giá trị (ví dụ: "product_type": "none" or "product_type": ["serum", "cleanser", "toner"])'
            )
            
            inst = inst.replace(
                'Nếu có quy trình thì BẮT BUỘC phải trích xuất product_type từ quy trình và ghép thành 1 chuỗi (ví dụ: "micellar, cleanser, antisun")!',
                'Nếu có quy trình thì BẮT BUỘC phải trích xuất product_type từ quy trình và xuất ra array (ví dụ: ["micellar", "cleanser", "antisun"])!'
            )
            
            inst = inst.replace(
                'QUAN TRỌNG: Khi Customer kể/liệt kê thói quen chăm sóc da hiện tại, Assistant BẮT BUỘC phải trích xuất TẤT CẢ các product_type tương ứng và ghép thành 1 chuỗi (ví dụ: "micellar, cleanser, antisun").',
                'QUAN TRỌNG: Khi Customer kể/liệt kê thói quen chăm sóc da hiện tại, Assistant BẮT BUỘC phải trích xuất TẤT CẢ các product_type tương ứng và xuất ra array (ví dụ: ["micellar", "cleanser", "antisun"]).'
            )
            
            # Change the example format back
            inst = inst.replace(
                '{\n  "vendor": "christina, dermoaroma",\n  "product_type": "serum, cleanser, micellar"\n}',
                '{\n  "vendor": ["christina", "dermoaroma"],\n  "product_type": ["serum", "cleanser", "micellar"]\n}'
            )

            # Change vendor back to array
            inst = inst.replace(
                '* "vendor": MỘT CHUỖI DUY NHẤT (string). Nếu có nhiều hãng, ngăn cách bằng dấu phẩy (ví dụ: "vendor": "christina, floslek")',
                '* "vendor": có thể là 1 giá trị, hoặc là array các giá trị (ví dụ: "vendor": "none" or "vendor": ["christina", "floslek"])'
            )

            n['properties']['instruction'] = inst
            print("Reverted GPT-4 Query Data to use array.")

        if 'branches' in n:
            for b_name, b_nodes in n['branches'].items():
                update_to_array(b_nodes)
        if 'sequence' in n:
            update_to_array(n['sequence'])

for node in data.get('sequence', []):
    if node.get('type') == 'flowSwitch':
        b2c_nodes = node.get('branches', {}).get('b2c_consult', [])
        update_to_array(b2c_nodes)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Finished reverting JSON string to array")
