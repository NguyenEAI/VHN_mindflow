"""
DEFINITIVE FIX for hallucination:
Replace the Format Product Info node in VHN_DauTien_Fixed.json
to use the EXACT SAME Handlebars template syntax as VHN_fixing.json.

Key change: Use {{api_raw_product_data[0].data}} and {{product_analyze.name}}
instead of raw Python variable references.
"""
import json

FIXING_FORMAT_PRODUCT_INFO = """PRODUCTS = {{api_raw_product_data[0].data}}
WISHLIST = {{product_analyze.name}}

# Tạo nội dung
content = ""
for product in PRODUCTS:
    title = product.get('name', '').replace("\\n", "").strip()
    i = 1
    for names in WISHLIST:
        if title == names:
            content += f"**{i}. {title}**\\n"
            
            # Kiểm tra và in ra ảnh nếu có
            if 'link_image' in product and product['link_image'] != 'N/A':
                content += f"![Ảnh sản phẩm]({product['link_image']})\\n"
            
            # Chỉ in giá tham khảo nếu có
            if 'price' in product and product['price'] != 'N/A':
                price_formatted = f"{product['price']:,}".replace(",", ".")
                content += f"**Giá tham khảo:** {price_formatted} VND\\n\\n"
                
            # Làm đẹp phần mô tả
            description = product.get('full_description', '').replace("\\n", "").strip()
            for keyword in ['Thành phần:', 'Công dụng:', 'Chỉ định:', 'Hướng dẫn sử dụng:']:
                description = description.replace(keyword, f"**{keyword}**")
            content += f"{description}\\n"
            
            # Lấy keywords giới thiệu sản phẩm
            if 'keywords' in product and product['keywords'] != 'N/A':
                keywords = product.get('keywords', '').replace("\\n", "").strip()
                content += f"**Đặc điểm nổi bật:** {keywords}\\n"
            
            # Kiểm tra và in ra link nếu có
            if 'link_product' in product and product['link_product'] != 'N/A':
                content += f"[Link sản phẩm]({product['link_product']})\\n"
            
            content += "\\n\\n"
            i += 1

# Trả về kết quả
print(content)"""

# Also fix the Format Wishlist to match VHN_fixing.json syntax
FIXING_FORMAT_WISHLIST = """PRODUCTS = {{api_raw_product_data[0].data}}

# Tạo nội dung rút gọn TỐI ĐA (Chỉ lấy Tên SP) cho LLM Analysis để tiết kiệm token
content = ""
for product in PRODUCTS:
    title = product.get('name', '').replace("\\n", "").strip()
    content += f"- {title}\\n"
    
print(content)"""


def fix_vhn(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    fixes = {'format_info': 0, 'format_wishlist': 0}
    
    def traverse(seq):
        for node in seq:
            # Fix Format Product Info (B2C)
            if node.get('type') == 'python' and node.get('properties', {}).get('varName') == 'session.extra.product_information':
                if node.get('name') == 'Format Product Info':  # B2C path
                    node['properties']['expression'] = FIXING_FORMAT_PRODUCT_INFO
                    fixes['format_info'] += 1
                    print(f"  Fixed: {node.get('name')}")
            
            # Fix Format Wishlist (B2C)
            if node.get('type') == 'python' and node.get('name') == 'Format Wishlist':
                if node.get('properties', {}).get('varName') == 'session.extra.product_wishlist':
                    node['properties']['expression'] = FIXING_FORMAT_WISHLIST
                    fixes['format_wishlist'] += 1
                    print(f"  Fixed: {node.get('name')}")
            
            if 'sequence' in node:
                traverse(node['sequence'])
            if 'branches' in node:
                for b in node['branches'].values():
                    traverse(b)
    
    traverse(data.get('sequence', []))
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nTotal: {fixes['format_info']} Format Info fixed, {fixes['format_wishlist']} Format Wishlist fixed.")

print("Applying anti-hallucination fix...")
fix_vhn(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json')
