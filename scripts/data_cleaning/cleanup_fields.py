import re

FILES = [
    r'c:\Users\Administrator\Desktop\Hoc_python\data\b2c_cleaned.txt',
    r'c:\Users\Administrator\Desktop\Hoc_python\data\b2b.txt',
]

# Cac pattern dong can xoa hoan toan (bat dau bang nhung gi nay)
REMOVE_LINE_PREFIXES = [
    '- **Sheet nguồn:**',
    '- **Giảm giá:**',
    '- **Combo:**',
    '- **is_salon_product:**',
    '- **Loại:**',          # phong truong hop con sot trong b2b
]

summary = open(r'c:\Users\Administrator\Desktop\Hoc_python\cleanup_result.txt', 'w', encoding='utf-8')
summary.write('=== KET QUA DON DEP FIELDS VA KHOANG TRANG ===\n\n')

for filepath in FILES:
    fname = filepath.split('\\')[-1]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    lines_before = len(lines)
    removed_lines = 0
    new_lines = []

    for line in lines:
        stripped = line.strip()
        
        # Kiem tra xem dong co thuoc nhom can xoa khong
        should_remove = any(stripped.startswith(prefix) for prefix in REMOVE_LINE_PREFIXES)
        
        if should_remove:
            removed_lines += 1
        else:
            new_lines.append(line)

    # Ghep lai va don dep khoang trang thua
    content = ''.join(new_lines)

    # Xoa nhieu dong trong lien tiep (3+ dong trong -> 1 dong trong)
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Xoa khoang trang cuoi dong (trailing spaces/tabs)
    content = re.sub(r'[ \t]+\n', '\n', content)

    # Xoa khoang trang dau dong thua (leading spaces tren dong chi co khoang trang)
    content = re.sub(r'\n[ \t]+\n', '\n\n', content)

    # Xoa dong trong ngay sau separator ---
    content = re.sub(r'\n---\n\n', '\n---\n', content)

    # Xoa dong trong ngay truoc separator ---
    content = re.sub(r'\n\n---\n', '\n---\n', content)

    # Xoa dong trong ngay sau tieu de ##
    content = re.sub(r'(## .+\n)\n+(-)', r'\1\2', content)

    content = content.strip() + '\n'

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    lines_after = content.count('\n')

    summary.write(f'File: {fname}\n')
    summary.write(f'  Dong truoc : {lines_before}\n')
    summary.write(f'  Dong sau   : {lines_after}\n')
    summary.write(f'  Giam       : {lines_before - lines_after} dong\n')
    summary.write(f'  Fields xoa : {removed_lines} dong\n\n')

summary.write('HOAN THANH!\n')
summary.close()
