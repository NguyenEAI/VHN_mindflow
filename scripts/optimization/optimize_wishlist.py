import json

with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

new_expression = """PRODUCTS = {{api_raw_product_data[0].data}}

# Tạo nội dung rút gọn cho LLM Analysis để tiết kiệm token
content = ""
for product in PRODUCTS:
    title = product.get('name', '').replace("\\n", "").strip()
    content += f"- Tên SP: {title}\\n"
    
    # Lấy mô tả ngắn gọn hoặc keywords thay vì full_description
    if 'description' in product and product['description'] != 'N/A':
        short_description = product.get('description', '').replace("\\n", "").strip()
        content += f"  Công dụng chính: {short_description}\\n"
    elif 'keywords' in product and product['keywords'] != 'N/A':
        keywords = product.get('keywords', '').replace("\\n", "").strip()
        content += f"  Keywords: {keywords}\\n"
        
    content += "\\n"
    
print(content)"""

updated = False
def update_wishlist_python(obj):
    global updated
    if isinstance(obj, dict):
        if obj.get('name') == 'Python' and obj.get('properties', {}).get('varName') == 'session.extra.product_wishlist':
            obj['properties']['expression'] = new_expression
            updated = True
            return True
        for k, v in obj.items():
            if update_wishlist_python(v):
                return True
    elif isinstance(obj, list):
        for v in obj:
            if update_wishlist_python(v):
                return True
    return False

update_wishlist_python(data)

if updated:
    print("Successfully updated product_wishlist Python node!")
    with open('VHN_fixing.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
else:
    print("Could not find the node.")
