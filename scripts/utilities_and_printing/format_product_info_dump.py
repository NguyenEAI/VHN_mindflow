import re

def normalize(s):
    if not isinstance(s, str): return ""
    s = re.sub(r'[^\w\s]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip().lower()

raw_data = api_raw_product_data
PRODUCTS = []
if isinstance(raw_data, list) and len(raw_data) > 0:
    if isinstance(raw_data[0], dict) and 'data' in raw_data[0]:
        PRODUCTS = raw_data[0]['data']
    elif isinstance(raw_data[0], dict):
        PRODUCTS = raw_data
elif isinstance(raw_data, dict) and 'data' in raw_data:
    PRODUCTS = raw_data['data']

WISHLIST = []
if isinstance(product_analyze, dict):
    WISHLIST = product_analyze.get('name', [])
elif isinstance(product_analyze, list):
    WISHLIST = product_analyze

if not isinstance(WISHLIST, list):
    WISHLIST = [WISHLIST]

content = ""
i = 1
for product in PRODUCTS:
    if not isinstance(product, dict):
        continue
    title = str(product.get('name', '')).replace("\n", "").strip()
    title_norm = normalize(title)
    
    matched = False
    for name in WISHLIST:
        name_norm = normalize(str(name))
        if title_norm == name_norm or name_norm in title_norm or title_norm in name_norm:
            matched = True
            break
            
    if matched:
        content += f"**{i}. {title}**\n"
        
        if 'link_image' in product and product['link_image'] and str(product['link_image']) != 'N/A':
            content += f"![Ảnh sản phẩm]({product['link_image']})\n"
        
        if 'price' in product and product['price'] and str(product['price']) != 'N/A':
            try:
                p_val = int(str(product['price']).replace('.', '').replace(',', ''))
                price_formatted = f"{p_val:,}".replace(",", ".")
            except:
                price_formatted = str(product['price'])
            content += f"**Giá tham khảo:** {price_formatted} VND\n\n"
            
        description = str(product.get('full_description', '')).replace("\n", "").strip()
        for keyword in ['Thành phần:', 'Công dụng:', 'Chỉ định:', 'Hướng dẫn sử dụng:']:
            description = description.replace(keyword, f"**{keyword}**")
        if description and description != 'N/A':
            content += f"{description}\n"
            
        if 'keywords' in product and product['keywords'] and str(product['keywords']) != 'N/A':
            keywords = str(product.get('keywords', '')).replace("\n", "").strip()
            content += f"**Đặc điểm nổi bật:** {keywords}\n"
            
        if 'link_product' in product and product['link_product'] and str(product['link_product']) != 'N/A':
            content += f"[Link sản phẩm]({product['link_product']})\n"
            
        content += "\n\n"
        i += 1

if not content:
    content = "empty"

import sys
sys.stdout.write(content)
