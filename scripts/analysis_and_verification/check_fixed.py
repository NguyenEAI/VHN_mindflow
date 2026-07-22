import json

with open(r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fs = next((n for n in data['sequence'] if n.get('type') == 'flowSwitch'), None)

print("B2C nodes:")
b2c = fs['branches'].get('b2c_consult', [])
for i, t in enumerate(b2c):
    print(f"[{i}] {t.get('type')} - {t.get('name')}")
    
print("\nB2B nodes:")
b2b = fs['branches'].get('b2b_consult', [])
for i, t in enumerate(b2b):
    print(f"[{i}] {t.get('type')} - {t.get('name')}")
