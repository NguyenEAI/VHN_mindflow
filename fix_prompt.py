import sys
path = 'VHN_DauTien_Fixed.json'
with open(path, 'r', encoding='utf-8') as f: data = f.read()
target = r'- Khi Customer mentions about \"line repair\", Assistant MUST chọn \"vendor\" là \"christina\" và remember to chọn \"product_type\" phù hợp với Customer.'
replacement = r'- Khi Customer mentions about \"line repair\", Assistant MUST chọn \"vendor\" là \"christina\" và BẮT BUỘC chọn \"product_type\" là \"none\" (do database chưa phân loại dòng này).'
if target in data:
    data = data.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f: f.write(data)
    print('Replaced successfully')
else:
    print('Target not found')
