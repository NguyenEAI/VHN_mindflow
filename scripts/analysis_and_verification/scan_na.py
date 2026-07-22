import re

f = open(r'c:\Users\Administrator\Desktop\Hoc_python\data\b2c_cleaned.txt', encoding='utf-8')
lines = f.readlines()
f.close()

patterns = {}
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if 'N/A' in stripped:
        patterns[stripped] = patterns.get(stripped, 0) + 1

out = open(r'c:\Users\Administrator\Desktop\Hoc_python\na_report.txt', 'w', encoding='utf-8')
out.write('=== CAC DONG CO N/A CON LAI TRONG b2c_cleaned.txt ===\n\n')
out.write(f'Tong so dong co N/A: {sum(patterns.values())}\n\n')
out.write('--- Chi tiet (noi dung dong : so lan xuat hien) ---\n')
for line, count in sorted(patterns.items(), key=lambda x: -x[1]):
    out.write(f'[{count:4d}x] {line}\n')
out.close()
