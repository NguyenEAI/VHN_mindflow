import csv, sys, json
sys.stdout.reconfigure(encoding='utf-8')
data = []
for row in csv.DictReader(open('sheet.csv', encoding='utf-8')):
    if 'Line Repair' in row['name']:
        data.append(f"{row['name']} -> type: {row['type']}")
with open('out.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(data))
