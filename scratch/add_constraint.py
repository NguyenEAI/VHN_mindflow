import json, codecs

# Text constraint that needs to be added
CONSTRAINT_TEXT = """\n\n# QUY TẮC BẮT BUỘC KHI TƯ VẤN BƯỚC SKINCARE:
- KHÔNG TỰ Ý ĐỀ XUẤT CÁC BƯỚC KHÁC (như tẩy tế bào chết, serum, toner, mặt nạ, v.v.) NẾU KHÁCH KHÔNG HỎI HOẶC KHÔNG SỬ DỤNG TRONG ROUTINE HIỆN TẠI.
- Nếu khách liệt kê chu trình hiện tại (ví dụ: tẩy trang, rửa mặt, kem chống nắng), CHỈ đề xuất các sản phẩm tương ứng với các bước đó.
- KHÔNG ĐƯỢC thêm bước mới vào chu trình của khách trừ khi khách chủ động hỏi "có cần thêm bước gì không".
"""

with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
    data = json.load(f)

for n in data.get('sequence', []):
    if n.get('type') == 'flowSwitch':
        for b in n.get('branches', {}).get('b2c_consult', []):
            if b.get('name') == 'AI Chuyên trách B2C':
                inst = b.get('properties', {}).get('instruction', '')
                if 'KHÔNG TỰ Ý ĐỀ XUẤT CÁC BƯỚC KHÁC' not in inst:
                    b['properties']['instruction'] = inst + CONSTRAINT_TEXT
                    print("Constraint added successfully!")

with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'w', 'utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

