"""
Kiem tra trung lap san pham trong B2C va B2B
- Trich xuat tung block san pham hoan chinh
- So sanh ID, ten, va noi dung
- Bao cao chi tiet
"""
import re
from collections import defaultdict

B2C_FILE = r'c:\Users\Administrator\Desktop\Hoc_python\data\b2c_cleaned.txt'
B2B_FILE = r'c:\Users\Administrator\Desktop\Hoc_python\data\b2b.txt'
OUT_FILE = r'c:\Users\Administrator\Desktop\Hoc_python\dup_report.txt'

def read_file(path):
    for enc in ['utf-8-sig', 'utf-8']:
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read()
        except:
            continue
    raise RuntimeError("Cannot read: " + path)

def extract_product_blocks(content):
    """
    Trich xuat tung block san pham.
    Moi block bat dau bang '## ' va ket thuc khi gap block khac hoac het file.
    Tra ve list cua dict: {id, name, block_text}
    """
    # Danh sach cac vi tri cua '## ' headers
    header_positions = [(m.start(), m.group(0)) for m in re.finditer(r'^## .+', content, re.MULTILINE)]
    
    products = []
    for i, (pos, header) in enumerate(header_positions):
        # Lay noi dung tu header nay den header tiep theo
        if i + 1 < len(header_positions):
            next_pos = header_positions[i + 1][0]
            block = content[pos:next_pos].strip()
        else:
            block = content[pos:].strip()
        
        # Lay ten san pham (header)
        name = header[3:].strip()  # bo '## '
        
        # Lay ID
        id_match = re.search(r'- \*\*ID:\*\*\s*(\d+)', block)
        pid = int(id_match.group(1)) if id_match else None
        
        products.append({
            'id': pid,
            'name': name,
            'block': block,
            'block_normalized': re.sub(r'\s+', ' ', block.lower().strip())
        })
    
    return products

def find_duplicates(products):
    """Tim cac san pham trung lap theo ID, theo ten, theo noi dung."""
    
    # Group by ID
    by_id = defaultdict(list)
    for i, p in enumerate(products):
        if p['id'] is not None:
            by_id[p['id']].append((i, p))
    
    # Group by name (normalized)
    by_name = defaultdict(list)
    for i, p in enumerate(products):
        norm_name = re.sub(r'\s+', ' ', p['name'].lower().strip())
        by_name[norm_name].append((i, p))
    
    # Group by content (normalized, bo link vi co the khac)
    def strip_links(text):
        text = re.sub(r'https?://\S+', '', text)
        return re.sub(r'\s+', ' ', text.lower().strip())
    
    by_content = defaultdict(list)
    for i, p in enumerate(products):
        key = strip_links(p['block'])
        by_content[key].append((i, p))
    
    # Tim duplicates
    id_dups = {k: v for k, v in by_id.items() if len(v) > 1}
    name_dups = {k: v for k, v in by_name.items() if len(v) > 1}
    content_dups = {k: v for k, v in by_content.items() if len(v) > 1}
    
    return id_dups, name_dups, content_dups

# === Doc file ===
b2c_content = read_file(B2C_FILE)
b2b_content = read_file(B2B_FILE)

b2c_products = extract_product_blocks(b2c_content)
b2b_products = extract_product_blocks(b2b_content)

# === Kiem tra ===
b2c_id_dups, b2c_name_dups, b2c_content_dups = find_duplicates(b2c_products)
b2b_id_dups, b2b_name_dups, b2b_content_dups = find_duplicates(b2b_products)

# === Cross-file check ===
b2c_all_ids = set(p['id'] for p in b2c_products if p['id'])
b2b_all_ids = set(p['id'] for p in b2b_products if p['id'])
cross_id_dups = b2c_all_ids & b2b_all_ids

b2c_all_names = set(re.sub(r'\s+', ' ', p['name'].lower().strip()) for p in b2c_products)
b2b_all_names = set(re.sub(r'\s+', ' ', p['name'].lower().strip()) for p in b2b_products)
cross_name_dups = b2c_all_names & b2b_all_names

# === Viet bao cao ===
lines = []
SEP = "=" * 70

lines.append(SEP)
lines.append("BAO CAO KIEM TRA TRUNG LAP SAN PHAM")
lines.append(SEP)
lines.append("")

# --- B2C Summary ---
lines.append("[B2C] Tong so block san pham trich duoc: " + str(len(b2c_products)))
lines.append("[B2C] ID bi trung lap (xuat hien >= 2 lan): " + str(len(b2c_id_dups)))
lines.append("[B2C] Ten bi trung lap (xuat hien >= 2 lan): " + str(len(b2c_name_dups)))
lines.append("[B2C] Block noi dung giong nhau hoan toan: " + str(len(b2c_content_dups)))
lines.append("")

# --- B2B Summary ---
lines.append("[B2B] Tong so block san pham trich duoc: " + str(len(b2b_products)))
lines.append("[B2B] ID bi trung lap (xuat hien >= 2 lan): " + str(len(b2b_id_dups)))
lines.append("[B2B] Ten bi trung lap (xuat hien >= 2 lan): " + str(len(b2b_name_dups)))
lines.append("[B2B] Block noi dung giong nhau hoan toan: " + str(len(b2b_content_dups)))
lines.append("")

# --- Cross-file ---
lines.append("[CROSS] ID xuat hien o CA 2 FILE: " + str(len(cross_id_dups)) + " ID")
if cross_id_dups:
    lines.append("  IDs: " + str(sorted(cross_id_dups)))
lines.append("[CROSS] Ten xuat hien o CA 2 FILE: " + str(len(cross_name_dups)) + " ten")
if cross_name_dups:
    for name in sorted(cross_name_dups):
        lines.append("  - " + name[:100])
lines.append("")

# --- B2C Details ---
lines.append(SEP)
lines.append("CHI TIET: B2C - ID TRUNG LAP")
lines.append(SEP)
if b2c_id_dups:
    for pid in sorted(b2c_id_dups.keys()):
        entries = b2c_id_dups[pid]
        lines.append("")
        lines.append("ID " + str(pid) + " -> xuat hien " + str(len(entries)) + " lan:")
        for idx, (_, p) in enumerate(entries):
            lines.append("  [" + str(idx+1) + "] Ten: " + p['name'][:90])
        # Kiem tra xem noi dung co giong nhau khong
        all_same = all(
            re.sub(r'\s+', ' ', e[1]['block'].lower()) == re.sub(r'\s+', ' ', entries[0][1]['block'].lower())
            for e in entries
        )
        lines.append("  -> Noi dung GIONG NHAU: " + ("YES" if all_same else "NO - CO KHAC BIET!"))
else:
    lines.append("  KHONG CO")

lines.append("")
lines.append(SEP)
lines.append("CHI TIET: B2B - ID TRUNG LAP")
lines.append(SEP)
if b2b_id_dups:
    for pid in sorted(b2b_id_dups.keys()):
        entries = b2b_id_dups[pid]
        lines.append("")
        lines.append("ID " + str(pid) + " -> xuat hien " + str(len(entries)) + " lan:")
        for idx, (_, p) in enumerate(entries):
            lines.append("  [" + str(idx+1) + "] Ten: " + p['name'][:90])
        all_same = all(
            re.sub(r'\s+', ' ', e[1]['block'].lower()) == re.sub(r'\s+', ' ', entries[0][1]['block'].lower())
            for e in entries
        )
        lines.append("  -> Noi dung GIONG NHAU: " + ("YES" if all_same else "NO - CO KHAC BIET!"))
else:
    lines.append("  KHONG CO")

# --- B2C Name-only dups (different ID same name) ---
lines.append("")
lines.append(SEP)
lines.append("CHI TIET: B2C - TEN TRUNG LAP (KHAC ID)")
lines.append(SEP)
name_only_dups = {k: v for k, v in b2c_name_dups.items()
                  if len(set(e[1]['id'] for e in v)) > 1}
if name_only_dups:
    for name, entries in sorted(name_only_dups.items()):
        lines.append("")
        lines.append("Ten: " + name[:90])
        for _, p in entries:
            lines.append("  ID " + str(p['id']) + ": " + p['name'][:90])
else:
    lines.append("  KHONG CO san pham nao co cung ten nhung khac ID trong B2C")

lines.append("")
lines.append(SEP)
lines.append("CHI TIET: B2B - TEN TRUNG LAP (KHAC ID)")
lines.append(SEP)
name_only_dups_b2b = {k: v for k, v in b2b_name_dups.items()
                      if len(set(e[1]['id'] for e in v)) > 1}
if name_only_dups_b2b:
    for name, entries in sorted(name_only_dups_b2b.items()):
        lines.append("")
        lines.append("Ten: " + name[:90])
        for _, p in entries:
            lines.append("  ID " + str(p['id']) + ": " + p['name'][:90])
else:
    lines.append("  KHONG CO san pham nao co cung ten nhung khac ID trong B2B")

# === Ghi file ===
with open(OUT_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

# === In ket qua ASCII ra console ===
print("=== KET QUA KIEM TRA ===")
print("B2C blocks:", len(b2c_products))
print("B2C ID dups:", len(b2c_id_dups))
print("B2C Name dups:", len(b2c_name_dups))
print("B2C Content dups:", len(b2c_content_dups))
print("")
print("B2B blocks:", len(b2b_products))
print("B2B ID dups:", len(b2b_id_dups))
print("B2B Name dups:", len(b2b_name_dups))
print("B2B Content dups:", len(b2b_content_dups))
print("")
print("Cross-file ID overlap:", len(cross_id_dups))
print("Cross-file Name overlap:", len(cross_name_dups))
print("")

# Confirm if ID dups are exact content copies
b2c_exact = sum(1 for pid, entries in b2c_id_dups.items()
    if all(re.sub(r'\s+', ' ', e[1]['block'].lower()) == re.sub(r'\s+', ' ', entries[0][1]['block'].lower()) for e in entries))
b2b_exact = sum(1 for pid, entries in b2b_id_dups.items()
    if all(re.sub(r'\s+', ' ', e[1]['block'].lower()) == re.sub(r'\s+', ' ', entries[0][1]['block'].lower()) for e in entries))

print("B2C: In", len(b2c_id_dups), "dup IDs,", b2c_exact, "are EXACT COPIES,", len(b2c_id_dups)-b2c_exact, "have DIFFERENT CONTENT")
print("B2B: In", len(b2b_id_dups), "dup IDs,", b2b_exact, "are EXACT COPIES,", len(b2b_id_dups)-b2b_exact, "have DIFFERENT CONTENT")
print("")
print("Report written to:", OUT_FILE)
