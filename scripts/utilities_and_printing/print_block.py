import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'c:\Users\Administrator\Desktop\Hoc_python\VHN_backup.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

sequence = data.get('sequence', [])
for idx, item in enumerate(sequence):
    if item.get('name') == 'Lấy thông tin sản phẩm':
        print(json.dumps(item, indent=2, ensure_ascii=False))
