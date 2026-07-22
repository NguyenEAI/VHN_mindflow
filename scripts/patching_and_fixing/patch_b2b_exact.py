"""
Fix B2B Exact Match Info to use Handlebars syntax like VHN_fixing.json
"""
import json

B2B_EXACT_MATCH = """PRODUCTS = {{api_raw_product_data[0].data}}
WISHLIST = {{product_analyze.name}}

content = ""
i = 1
for product in PRODUCTS:
    title = product.get('name', '').replace("\\n", "").strip()
    for names in WISHLIST:
        if title == names:
            content += f"**{i}. {title}**\\n"
            
            if 'link_image' in product and product['link_image'] != 'N/A':
                content += f"![Ảnh sản phẩm]({product['link_image']})\\n"
            
            if 'price' in product and product['price'] != 'N/A':
                price_formatted = f"{product['price']:,}".replace(",", ".")
                content += f"**Giá tham khảo:** {price_formatted} VND\\n\\n"
                
            description = product.get('full_description', '').replace("\\n", "").strip()
            for keyword in ['Thành phần:', 'Công dụng:', 'Chỉ định:', 'Hướng dẫn sử dụng:']:
                description = description.replace(keyword, f"**{keyword}**")
            content += f"{description}\\n"
            
            if 'keywords' in product and product['keywords'] != 'N/A':
                keywords = product.get('keywords', '').replace("\\n", "").strip()
                content += f"**Đặc điểm nổi bật:** {keywords}\\n"
            
            if 'link_product' in product and product['link_product'] != 'N/A':
                content += f"[Link sản phẩm]({product['link_product']})\\n"
            
            content += "\\n\\n"
            i += 1

print(content)"""

def fix_vhn(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    fixed = 0
    
    def traverse(seq):
        nonlocal fixed
        for node in seq:
            if (node.get('type') == 'python' and 
                node.get('name') == 'Exact Match Info' and
                node.get('properties', {}).get('varName') == 'session.extra.product_information'):
                node['properties']['expression'] = B2B_EXACT_MATCH
                fixed += 1
                print(f"  Fixed: {node.get('name')}")
            
            if 'sequence' in node:
                traverse(node['sequence'])
            if 'branches' in node:
                for b in node['branches'].values():
                    traverse(b)
    
    traverse(data.get('sequence', []))
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nTotal: {fixed} nodes fixed.")

print("Fixing B2B Exact Match Info...")
fix_vhn(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json')
