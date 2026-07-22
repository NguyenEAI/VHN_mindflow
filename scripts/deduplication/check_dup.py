from collections import Counter

f = open(r'c:\Users\Administrator\Desktop\Hoc_python\data\b2c_cleaned.txt', encoding='utf-8')
content = f.read()
f.close()

lines = content.split('\n')
product_headers = [(i, l) for i, l in enumerate(lines) if l.startswith('## ')]
names = [l[3:] for _, l in product_headers]
name_count = Counter(names)
dups = {k: v for k, v in name_count.items() if v > 1}

out = open('dup_report.txt', 'w', encoding='utf-8')
out.write(f'Tong so dong: {len(lines)}\n')
out.write(f'Tong tieu de ##: {len(product_headers)}\n')
out.write(f'San pham duy nhat: {len(set(names))}\n')
out.write(f'San pham trung lap: {len(dups)}\n\n')
out.write('--- Chi tiet ---\n')
for name, count in list(dups.items())[:5]:
    positions = [i+1 for i, l in product_headers if l[3:] == name]
    out.write(f'[{count}x] lines {positions} - {name[:70]}\n')
out.close()
