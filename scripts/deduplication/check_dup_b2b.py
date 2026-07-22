from collections import Counter

f = open(r'c:\Users\Administrator\Desktop\Hoc_python\data\b2b.txt', encoding='utf-8')
content = f.read()
f.close()

lines = content.split('\n')
product_headers = [(i+1, l) for i, l in enumerate(lines) if l.startswith('## ')]
names = [l[3:] for _, l in product_headers]
name_count = Counter(names)
dups = {k: v for k, v in name_count.items() if v > 1}

result = open(r'c:\Users\Administrator\Desktop\Hoc_python\b2b_dup_report.txt', 'w', encoding='utf-8')
result.write(f'Tong so dong: {len(lines)}\n')
result.write(f'Tong tieu de ##: {len(product_headers)}\n')
result.write(f'San pham duy nhat: {len(set(names))}\n')
result.write(f'San pham trung lap: {len(dups)}\n\n')
result.write('--- Vi du 5 san pham dau ---\n')
for name, count in list(dups.items())[:5]:
    positions = [i for i, l in product_headers if l[3:] == name]
    result.write(f'[{count}x] lines {positions} - {name[:70]}\n')
result.close()
