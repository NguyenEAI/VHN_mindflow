import re
import sys

# =============================================
# Doc file B2C
# =============================================
b2c_file = r'c:\Users\Administrator\Desktop\Hoc_python\data\b2c_cleaned.txt'
b2b_file = r'c:\Users\Administrator\Desktop\Hoc_python\data\b2b.txt'

def read_file(path):
    for enc in ['utf-8-sig', 'utf-8', 'utf-16']:
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read()
        except Exception:
            continue
    raise RuntimeError(f"Cannot read {path}")

b2c_content = read_file(b2c_file)
b2b_content = read_file(b2b_file)

def extract_products(content, label):
    """Trich xuat tat ca san pham: tra ve dict {id: [ten_sp, ...]}"""
    # Split theo block ---
    blocks = re.split(r'\n---\n|\r\n---\r\n', content)
    products = {}
    for block in blocks:
        block = block.strip()
        name_match = re.search(r'^## (.+)', block, re.MULTILINE)
        id_match = re.search(r'-\s*\*\*ID:\*\*\s*(\d+)', block)
        if name_match and id_match:
            name = name_match.group(1).strip()
            pid = int(id_match.group(1))
            if pid in products:
                products[pid].append(name)
            else:
                products[pid] = [name]
    return products

b2c_products = extract_products(b2c_content, 'B2C')
b2b_products = extract_products(b2b_content, 'B2B')

output = []
output.append("=" * 60)
output.append("KIEM TRA TRUNG LAP SAN PHAM")
output.append("=" * 60)

# === 1. Kiem tra trung lap ben trong B2C ===
output.append("")
output.append("=== FILE B2C ===")
output.append(f"Tong so unique ID trong B2C: {len(b2c_products)}")

b2c_dups = {k: v for k, v in b2c_products.items() if len(v) > 1}
if b2c_dups:
    output.append(f"!!! CO {len(b2c_dups)} ID TRUNG LAP BEN TRONG B2C:")
    for pid, names in sorted(b2c_dups.items()):
        output.append(f"  ID {pid} xuat hien {len(names)} lan:")
        for n in names:
            output.append(f"    -> {n}")
else:
    output.append("  OK: Khong co ID trung lap ben trong B2C")

# === 2. Kiem tra trung lap ben trong B2B ===
output.append("")
output.append("=== FILE B2B ===")
output.append(f"Tong so unique ID trong B2B: {len(b2b_products)}")

b2b_dups = {k: v for k, v in b2b_products.items() if len(v) > 1}
if b2b_dups:
    output.append(f"!!! CO {len(b2b_dups)} ID TRUNG LAP BEN TRONG B2B:")
    for pid, names in sorted(b2b_dups.items()):
        output.append(f"  ID {pid} xuat hien {len(names)} lan:")
        for n in names:
            output.append(f"    -> {n}")
else:
    output.append("  OK: Khong co ID trung lap ben trong B2B")

# === 3. Kiem tra ID xuat hien o ca 2 file ===
output.append("")
output.append("=== ID XUAT HIEN O CA 2 FILE B2C va B2B ===")
common_ids = set(b2c_products.keys()) & set(b2b_products.keys())
if common_ids:
    output.append(f"!!! CO {len(common_ids)} ID XUAT HIEN O CA 2 FILE:")
    for pid in sorted(common_ids):
        output.append(f"  ID {pid}:")
        output.append(f"    B2C: {b2c_products[pid][0]}")
        output.append(f"    B2B: {b2b_products[pid][0]}")
else:
    output.append("  OK: Khong co ID nao xuat hien o ca 2 file")

# === 4. Kiem tra trung lap theo ten (partial match) ===
output.append("")
output.append("=== KIEM TRA TEN GIONG NHAU GIUA 2 FILE ===")

def normalize_name(s):
    # Bo "Step X:", "- X ", "B2B/B2C prefix", lowercase, xoa space thua
    s = re.sub(r'Step \d+[a-zA-Z]?:\s*', '', s)
    s = re.sub(r'-\s*\d+[a-zA-Z]?\s+', ' ', s)
    s = re.sub(r'\s+', ' ', s.lower().strip())
    return s

b2c_name_map = {}
for pid, names in b2c_products.items():
    norm = normalize_name(names[0])
    b2c_name_map[norm] = (pid, names[0])

b2b_name_map = {}
for pid, names in b2b_products.items():
    norm = normalize_name(names[0])
    b2b_name_map[norm] = (pid, names[0])

common_names = set(b2c_name_map.keys()) & set(b2b_name_map.keys())
if common_names:
    output.append(f"!!! CO {len(common_names)} TEN TRUNG NHAU (sau normalize):")
    for name in sorted(common_names):
        b2c_pid, b2c_name = b2c_name_map[name]
        b2b_pid, b2b_name = b2b_name_map[name]
        output.append(f"  B2C ID={b2c_pid} vs B2B ID={b2b_pid}")
        output.append(f"    B2C: {b2c_name}")
        output.append(f"    B2B: {b2b_name}")
else:
    output.append("  OK: Khong co ten trung nhau (sau normalize) giua 2 file")

# Ghi ra file ket qua
result_text = "\n".join(output)
result_file = r'c:\Users\Administrator\Desktop\Hoc_python\duplicate_check_result.txt'
with open(result_file, 'w', encoding='utf-8') as f:
    f.write(result_text)

print("DONE! Ket qua da duoc ghi ra:", result_file)
print("")
print(result_text)
