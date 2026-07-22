import re

INPUT_FILE = r'c:\Users\Administrator\Desktop\Hoc_python\data\b2b.txt'

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

lines_before = content.count('\n')

# Tach thanh cac blocks phan cach bang \n---\n
parts = re.split(r'\n---\n', content)
file_header = parts[0]
product_blocks = parts[1:]

# Deduplicate: giu ban dau tien, bo ban trung
seen_titles = set()
unique_blocks = []
skipped = 0

for block in product_blocks:
    title_match = re.search(r'^## (.+)$', block, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
        if title not in seen_titles:
            seen_titles.add(title)
            unique_blocks.append(block)
        else:
            skipped += 1
    else:
        unique_blocks.append(block)

# Ghep lai
new_content = file_header + '\n---\n' + '\n---\n'.join(unique_blocks)
new_content = re.sub(r'\n{3,}', '\n\n', new_content)
new_content = new_content.strip() + '\n'

with open(INPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(new_content)

lines_after = new_content.count('\n')

result = open(r'c:\Users\Administrator\Desktop\Hoc_python\b2b_dedup_result.txt', 'w')
result.write('=== KET QUA LOAI BO TRUNG LAP b2b.txt ===\n\n')
result.write(f'Tong blocks truoc: {len(product_blocks)}\n')
result.write(f'Tong blocks sau : {len(unique_blocks)}\n')
result.write(f'Da xoa          : {skipped} san pham trung\n')
result.write(f'\nDong truoc: {lines_before}\n')
result.write(f'Dong sau  : {lines_after}\n')
result.write(f'Giam      : {lines_before - lines_after} dong\n')
result.write('\nHOAN THANH! b2b.txt da duoc cap nhat.\n')
result.close()
