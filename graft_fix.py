import json

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

fixing = load_json(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_fixing.json')
target = load_json(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json')

def find_node(seq, name, type_str):
    for i, node in enumerate(seq):
        if node.get('name') == name and node.get('type') == type_str:
            return seq, i, node
        if 'sequence' in node:
            r = find_node(node['sequence'], name, type_str)
            if r: return r
        if 'branches' in node:
            for b in node['branches'].values():
                r = find_node(b, name, type_str)
                if r: return r
    return None

# Find Sheet Product in fixing
r_fix = find_node(fixing.get('sequence', []), 'Sheet Product', 'block')
if not r_fix:
    print("Could not find Sheet Product in fixing")
    exit(1)
seq_fix, idx_fix, sheet_product_fixing = r_fix

# Find Sheet Product in target
r_tgt = find_node(target.get('sequence', []), 'Sheet Product', 'block')
if not r_tgt:
    print("Could not find Sheet Product in target")
    exit(1)
seq_tgt, idx_tgt, sheet_product_tgt = r_tgt

# We will apply robust matching to Format Product Info inside sheet_product_fixing
r_fpi = find_node([sheet_product_fixing], 'Format Product Info', 'python')
if not r_fpi:
    # It might just be an unnamed Python node, let's search by varName session.extra.product_information
    def find_python_by_var(seq, var_name):
        for node in seq:
            if node.get('type') == 'python' and node.get('properties', {}).get('varName') == var_name:
                return node
            if 'sequence' in node:
                r = find_python_by_var(node['sequence'], var_name)
                if r: return r
            if 'branches' in node:
                for b in node['branches'].values():
                    r = find_python_by_var(b, var_name)
                    if r: return r
        return None
    fpi_node = find_python_by_var([sheet_product_fixing], 'session.extra.product_information')
else:
    fpi_node = r_fpi[2]

robust_code = """
PRODUCTS = {{api_raw_product_data[0].data}}
WISHLIST = {{product_analyze.name}}

content = ""
i = 1

for product in PRODUCTS:
    title = product.get('name', '').replace("\\n", "").strip()
    title_lower = title.lower()
    
    # Robust matching
    match_found = False
    for names in WISHLIST:
        names_lower = names.strip().lower()
        if names_lower in title_lower or title_lower in names_lower:
            match_found = True
            break
            
    if match_found:
        content += f"**{i}. {title}**\\n"
        
        if 'link_image' in product and product['link_image'] != 'N/A':
            content += f"![Ảnh sản phẩm]({product['link_image']})\\n"
            
        if 'price' in product and product['price'] != 'N/A':
            try:
                price_num = float(product['price'].replace(',', '').replace('.', ''))
                price_formatted = f"{int(price_num):,}".replace(",", ".")
            except:
                price_formatted = product['price']
            content += f"**Giá bán lẻ:** {price_formatted} VNĐ\\n\\n"
            
        description = product.get('full_description', '').replace("\\n", "").strip()
        for keyword in ['Thành phần:', 'Công dụng:', 'Chỉ định:', 'Hướng dẫn sử dụng:', 'Cách dùng:']:
            description = description.replace(keyword, f"**{keyword}**")
        content += f"{description}\\n"
        
        if 'keywords' in product and product['keywords'] != 'N/A':
            keywords = product.get('keywords', '').replace("\\n", "").strip()
            content += f"**Đặc điểm nổi bật:** {keywords}\\n"
            
        if 'link_product' in product and product['link_product'] != 'N/A':
            content += f"[Link sản phẩm]({product['link_product']})\\n"
            
        content += "\\n\\n"
        i += 1

print(content)
"""

if fpi_node:
    fpi_node['properties']['expression'] = robust_code
    print("Injected robust matching code.")
else:
    print("Could not find python node for product_information")

# Replace in target
seq_tgt[idx_tgt] = sheet_product_fixing

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'w', encoding='utf-8') as f:
    json.dump(target, f, ensure_ascii=False, indent=2)

print("Grafted successfully!")
