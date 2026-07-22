import re

INPUT_FILE = r'c:\Users\Administrator\Desktop\Hoc_python\data\b2c_cleaned.txt'

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Dem truoc khi xu ly
c1 = len(re.findall(r'- \*\*Lo\u1ea1i:\*\* N/A', content))
c2 = len(re.findall(r'- \*\*Gi\u00e1 g\u1ed1c:\*\* N/A', content))
c3 = len(re.findall(r'- \*\*Gi\u00e1 b\u00e1n:\*\* N/A', content))

lines_before = content.count('\n')

# 1. Xoa dong "- **Loai:** N/A"
content = re.sub(r'\n- \*\*Lo\u1ea1i:\*\* N/A[ \t]*', '', content)

# 2. Xoa dong "- **Gia goc:** N/A"
content = re.sub(r'\n- \*\*Gi\u00e1 g\u1ed1c:\*\* N/A[ \t]*', '', content)

# 3. Doi "- **Gia ban:** N/A" -> "- **Gia ban:** LIEN HE"
old = '- **Gi\u00e1 b\u00e1n:** N/A'
new = '- **Gi\u00e1 b\u00e1n:** LI\u00caN H\u1ec6'
content = content.replace(old, new)

lines_after = content.count('\n')

with open(INPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

result = open(r'c:\Users\Administrator\Desktop\Hoc_python\fix_na_result.txt', 'w')
result.write('=== KET QUA XU LY N/A ===\n\n')
result.write(f'Xoa [Loai N/A]    : {c1}\n')
result.write(f'Xoa [Gia goc N/A] : {c2}\n')
result.write(f'Doi [Gia ban N/A] -> LIEN HE: {c3}\n')
result.write(f'\nDong truoc: {lines_before}\n')
result.write(f'Dong sau  : {lines_after}\n')
result.write(f'Giam      : {lines_before - lines_after} dong\n')
result.write('\nHOAN THANH! File da duoc cap nhat.\n')
result.close()
