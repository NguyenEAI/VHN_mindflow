import re

INPUT_FILE = r'c:\Users\Administrator\Desktop\Hoc_python\data\b2c_cleaned.txt'

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Tach file thanh cac khoi san pham (phan cach bang \n---\n)
# Giu header cua file (dong dau truoc san pham dau tien)
# Pattern: moi record bat dau bang "---\n## "

# Tach ra header tong (truoc san pham dau)
parts = re.split(r'\n---\n', content)

# Phan dau tien la header cua file (khong phai san pham)
file_header = parts[0]  # "# DANH SACH SAN PHAM B2C..."

# Cac phan con lai la cac san pham
product_blocks = parts[1:]



# Deduplicate: giu ban dau tien xuat hien, bo ban trung
seen_titles = set()
unique_blocks = []
skipped = 0

for block in product_blocks:
    # Tim tieu de san pham (dong bat dau bang ## )
    title_match = re.search(r'^## (.+)$', block, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
        if title not in seen_titles:
            seen_titles.add(title)
            unique_blocks.append(block)
        else:
            skipped += 1
    else:
        # Block khong co tieu de (co the la header phu), giu lai
        unique_blocks.append(block)



# Ghep lai thanh noi dung moi
new_content = file_header + '\n---\n' + '\n---\n'.join(unique_blocks)

# Xoa nhieu dong trang lien tiep (don dep sau khi ghep)
new_content = re.sub(r'\n{3,}', '\n\n', new_content)
new_content = new_content.strip() + '\n'

with open(INPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(new_content)

lines_before = content.count('\n')
lines_after = new_content.count('\n')

result = open('dedup_result.txt', 'w')
result.write('=== KET QUA LOAI BO TRUNG LAP ===\n\n')
result.write(f'Tong blocks truoc: {len(product_blocks)}\n')
result.write(f'Tong blocks sau : {len(unique_blocks)}\n')
result.write(f'Da xoa          : {skipped} san pham trung\n')
result.write(f'\nDong truoc: {lines_before}\n')
result.write(f'Dong sau  : {lines_after}\n')
result.write(f'Giam      : {lines_before - lines_after} dong\n')
result.write('\nHOAN THANH! b2c_cleaned.txt da duoc cap nhat.\n')
result.close()
