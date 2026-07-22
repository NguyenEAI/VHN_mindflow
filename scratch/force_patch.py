import codecs

file_path = 'c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json'

with codecs.open(file_path, 'r', 'utf-8') as f:
    text = f.read()

target = "→ BẮT BUỘC đề xuất ĐỦ 4 SẢN PHẨM tương ứng 4 bước: (1) Tẩy trang, (2) Sữa rửa mặt, (3) Serum, (4) Kem chống nắng."

rule = """→ BẮT BUỘC đề xuất ĐỦ 4 SẢN PHẨM tương ứng 4 bước: (1) Tẩy trang, (2) Sữa rửa mặt, (3) Serum, (4) Kem chống nắng.

## QUY TẮC CẤM TỰ Ý THÊM BƯỚC:
TUYỆT ĐỐI KHÔNG tự ý đề xuất thêm hoặc bổ sung bất kỳ bước skincare nào (ví dụ: tẩy tế bào chết, serum đặc trị, mặt nạ, toner...) nếu Customer KHÔNG chủ động nhắc đến bước đó trong thói quen hiện tại của họ. 
CHỈ ĐƯỢC PHÉP chọn các sản phẩm thuộc ĐÚNG các loại mà khách đang dùng, và các sản phẩm đó phải có công dụng/thành phần phù hợp để giải quyết tình trạng da của khách (ví dụ khách nói chỉ dùng tẩy trang, sữa rửa mặt, kem chống nắng và da bị mụn -> chỉ đề xuất đúng 3 món đó nhưng dành cho da mụn. TUYỆT ĐỐI KHÔNG đề xuất thêm tẩy tế bào chết)."""

if "QUY TẮC CẤM TỰ Ý THÊM BƯỚC" in text:
    print("Already patched!")
elif target in text:
    new_text = text.replace(target, rule)
    with codecs.open(file_path, 'w', 'utf-8') as fw:
        fw.write(new_text)
    print("Patched successfully!")
else:
    print("Target not found!")
