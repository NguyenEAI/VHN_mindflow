# -*- coding: utf-8 -*-
"""
Script làm sạch dữ liệu b2c.txt
File nguồn : data/b2c.txt
File kết quả: data/b2c_cleaned.txt
"""

import re
import os

INPUT_FILE  = r'c:\Users\Administrator\Desktop\Hoc_python\data\b2c.txt'
OUTPUT_FILE = r'c:\Users\Administrator\Desktop\Hoc_python\data\b2c_cleaned.txt'

# ─────────────────────────────────────────────
# Đọc file
# ─────────────────────────────────────────────
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

original_lines = content.count('\n')
original_size  = len(content)
stats = {}

# ─────────────────────────────────────────────
# BƯỚC 0: Xóa các section chỉ chứa N/A
# ─────────────────────────────────────────────
# Các pattern dưới đây match chuỗi "\n### <Header>\nN/A"
# (có thể có trailing space sau N/A)
# Sau khi xóa, bước 3 sẽ dọn dẹp các dòng trắng thừa còn lại.

na_sections = [
    ('Công dụng',              'xoa_cong_dung'),
    ('Chỉ định',           'xoa_chi_dinh'),
    ('Hướng dẫn sử dụng', 'xoa_huong_dan'),
    ('Key giới thiệu sản phẩm', 'xoa_key_intro'),
]

for section, stat_key in na_sections:
    pattern = r'\n### ' + re.escape(section) + r'\nN/A[ \t]*'
    count = len(re.findall(pattern, content))
    stats[stat_key] = count
    content = re.sub(pattern, '', content)

# Links: chỉ xóa khi CẢ HAI link đều là N/A
links_na_pattern = (
    r'\n### Links\n'
    r'- \*\*Link sản phẩm:\*\* N/A[ \t]*\n'
    r'- \*\*Link hình ảnh:\*\* N/A[ \t]*'
)
count = len(re.findall(links_na_pattern, content))
stats['xoa_links_na'] = count
content = re.sub(links_na_pattern, '', content)

# ─────────────────────────────────────────────
# BƯỚC 1: Trim trailing whitespace mỗi dòng
# ─────────────────────────────────────────────
lines = content.split('\n')
trimmed_count = sum(1 for l in lines if l != l.rstrip())
lines = [l.rstrip() for l in lines]
content = '\n'.join(lines)
stats['Trim trailing whitespace (dòng)'] = trimmed_count

# ─────────────────────────────────────────────
# BƯỚC 2: Xóa leading whitespace thừa trong danh sách thành phần
# Dòng " - xxx" hoặc "   - xxx" → "- xxx"
# ─────────────────────────────────────────────
count = len(re.findall(r'\n[ \t]+- ', content))
stats['Sửa leading whitespace (- item)'] = count
content = re.sub(r'\n[ \t]+- ', '\n- ', content)

# ─────────────────────────────────────────────
# BƯỚC 3: Thu gọn nhiều dòng trắng liên tiếp → tối đa 1 dòng trắng
# ─────────────────────────────────────────────
before = len(re.findall(r'\n{3,}', content))
content = re.sub(r'\n{3,}', '\n\n', content)
stats['Thu gọn dòng trắng thừa (3+→1)'] = before

# ─────────────────────────────────────────────
# BƯỚC 4: Xóa label lặp trong các section
# Ví dụ: "### Công dụng\nCông dụng: \n" → "### Công dụng\n"
# ─────────────────────────────────────────────
duplicate_labels = [
    (r'(### Công dụng\n)Công dụng:[ \t]*\n',         r'\1'),
    (r'(### Chỉ định\n)Chỉ định:[ \t]*\n',            r'\1'),
    (r'(### Hướng dẫn sử dụng\n)Hướng dẫn sử dụng:[ \t]*\n', r'\1'),
]
dup_total = 0
for pattern, repl in duplicate_labels:
    c = len(re.findall(pattern, content))
    dup_total += c
    content = re.sub(pattern, repl, content)
stats['Xóa label lặp (Công dụng/Chỉ định/HDSD)'] = dup_total

# ─────────────────────────────────────────────
# BƯỚC 5: Đảm bảo có dòng trắng trước "Dung tích:"
# ─────────────────────────────────────────────
count = len(re.findall(r'([^\n])\n(Dung tích:)', content))
content = re.sub(r'([^\n])\n(Dung tích:)', r'\1\n\n\2', content)
stats['Thêm dòng trắng trước Dung tích'] = count

# ─────────────────────────────────────────────
# BƯỚC 6: Thêm dòng trắng giữa các đoạn trong Mô tả đầy đủ
# Nếu "Công dụng:" / "Chỉ định:" / "Hướng dẫn sử dụng:"
# bị dính liền vào dòng trên (không có dòng trắng trước)
# ─────────────────────────────────────────────
sep_patterns = [
    r'([^\n])\n(Công dụng:[ \t]*\n)',
    r'([^\n])\n(Chỉ định:[ \t]*\n)',
    r'([^\n])\n(Hướng dẫn sử dụng:[ \t]*\n)',
]
sep_total = 0
for pattern in sep_patterns:
    c = len(re.findall(pattern, content))
    sep_total += c
    content = re.sub(pattern, r'\1\n\n\2', content)
stats['Thêm dòng trắng trước Công dụng/Chỉ định/HDSD'] = sep_total

# ─────────────────────────────────────────────
# BƯỚC 7: Xóa dòng "description" placeholder
# ─────────────────────────────────────────────
count = len(re.findall(r'\ndescription[ \t]*\n', content))
content = re.sub(r'\ndescription[ \t]*\n', '\n', content)
stats['Xóa placeholder "description"'] = count

# ─────────────────────────────────────────────
# Dọn dẹp lần cuối
# ─────────────────────────────────────────────
# Thu gọn dòng trắng thừa lần 2 (do các bước trên có thể sinh ra)
content = re.sub(r'\n{3,}', '\n\n', content)
# Đảm bảo file kết thúc bằng 1 dòng trắng
content = content.strip() + '\n'

# ─────────────────────────────────────────────
# Ghi file
# ─────────────────────────────────────────────
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

final_lines = content.count('\n')
final_size  = len(content)

# ─────────────────────────────────────────────
# Bao cao ket qua (ASCII only for Windows console)
# ─────────────────────────────────────────────
print("=" * 55)
print("  KET QUA LAM SACH DU LIEU b2c.txt")
print("=" * 55)
print(f"  File nguon : {INPUT_FILE}")
print(f"  File ket qua: {OUTPUT_FILE}")
print("-" * 55)
print(f"  Dong ban dau   : {original_lines:,}")
print(f"  Dong sau xu ly : {final_lines:,}")
print(f"  Giam           : {original_lines - final_lines:,} dong "
      f"({(original_lines-final_lines)/original_lines*100:.1f}%)")
print(f"  Size ban dau : {original_size/1024:.1f} KB")
print(f"  Size sau     : {final_size/1024:.1f} KB")
print(f"  Giam         : {(original_size-final_size)/1024:.1f} KB "
      f"({(original_size-final_size)/original_size*100:.1f}%)")
print("-" * 55)
print("  Chi tiet cac thay doi:")
for key, val in stats.items():
    print(f"  OK [{key}]: {val:,}")
print("=" * 55)
print("  HOAN THANH!")
print("=" * 55)
