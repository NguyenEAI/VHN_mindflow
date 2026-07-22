import re
from collections import Counter

b2c_file = r'c:\Users\Administrator\Desktop\Hoc_python\data\b2c_cleaned.txt'
b2b_file = r'c:\Users\Administrator\Desktop\Hoc_python\data\b2b.txt'
out_file = r'c:\Users\Administrator\Desktop\Hoc_python\count_result.txt'

def read_file(path):
    for enc in ['utf-8-sig', 'utf-8']:
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read()
        except:
            continue
    raise RuntimeError(f"Cannot read {path}")

b2c_content = read_file(b2c_file)
b2b_content = read_file(b2b_file)

b2c_headers = re.findall(r'^## .+', b2c_content, re.MULTILINE)
b2b_headers = re.findall(r'^## .+', b2b_content, re.MULTILINE)
b2c_ids = re.findall(r'- \*\*ID:\*\*\s*(\d+)', b2c_content)
b2b_ids = re.findall(r'- \*\*ID:\*\*\s*(\d+)', b2b_content)

b2c_counter = Counter(b2c_ids)
b2b_counter = Counter(b2b_ids)
b2c_dups = [(k, v) for k, v in b2c_counter.items() if v > 1]
b2b_dups = [(k, v) for k, v in b2b_counter.items() if v > 1]
common_ids = set(b2c_ids) & set(b2b_ids)

# Build name maps too
b2c_name_pattern = re.findall(r'^## (.+)', b2c_content, re.MULTILINE)
b2b_name_pattern = re.findall(r'^## (.+)', b2b_content, re.MULTILINE)
b2c_name_counter = Counter(b2c_name_pattern)
b2b_name_counter = Counter(b2b_name_pattern)
b2c_name_dups = [(k, v) for k, v in b2c_name_counter.items() if v > 1]
b2b_name_dups = [(k, v) for k, v in b2b_name_counter.items() if v > 1]

# Cross-file name comparison (normalize)
def norm(s):
    s = re.sub(r'Step \d+[a-zA-Z]?:\s*', '', s)
    s = re.sub(r'[-]\s*\d+[a-zA-Z]?\s+', ' ', s)
    return re.sub(r'\s+', ' ', s.lower().strip())

b2c_norm_names = set(norm(n) for n in b2c_name_pattern)
b2b_norm_names = set(norm(n) for n in b2b_name_pattern)
cross_dups = b2c_norm_names & b2b_norm_names

lines = []
lines.append("=" * 60)
lines.append("PHAN TICH TRUNG LAP SAN PHAM")
lines.append("=" * 60)
lines.append("")
lines.append("[B2C] So ## headers (san pham): " + str(len(b2c_headers)))
lines.append("[B2C] So ID entries: " + str(len(b2c_ids)))
lines.append("[B2C] So unique ID: " + str(len(set(b2c_ids))))
lines.append("[B2C] So ID bi lap (>1 lan): " + str(len(b2c_dups)))
lines.append("")
lines.append("[B2B] So ## headers (san pham): " + str(len(b2b_headers)))
lines.append("[B2B] So ID entries: " + str(len(b2b_ids)))
lines.append("[B2B] So unique ID: " + str(len(set(b2b_ids))))
lines.append("[B2B] So ID bi lap (>1 lan): " + str(len(b2b_dups)))
lines.append("")
lines.append("[CROSS] ID xuat hien o CA 2 file: " + str(sorted(common_ids, key=int)))
lines.append("[CROSS] Ten tuong dong sau normalize: " + str(len(cross_dups)) + " sp")
lines.append("")

lines.append("--- B2C ID TRUNG LAP ---")
if b2c_dups:
    for k, v in sorted(b2c_dups, key=lambda x: int(x[0])):
        lines.append("  ID " + k + ": " + str(v) + " lan")
else:
    lines.append("  KHONG CO")

lines.append("")
lines.append("--- B2B ID TRUNG LAP ---")
if b2b_dups:
    for k, v in sorted(b2b_dups, key=lambda x: int(x[0])):
        lines.append("  ID " + k + ": " + str(v) + " lan")
else:
    lines.append("  KHONG CO")

lines.append("")
lines.append("--- B2C TEN TRUNG LAP ---")
if b2c_name_dups:
    for k, v in sorted(b2c_name_dups):
        lines.append("  [" + str(v) + "x] " + k[:100])
else:
    lines.append("  KHONG CO")

lines.append("")
lines.append("--- B2B TEN TRUNG LAP ---")
if b2b_name_dups:
    for k, v in sorted(b2b_name_dups):
        lines.append("  [" + str(v) + "x] " + k[:100])
else:
    lines.append("  KHONG CO")

with open(out_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

# Also print ASCII only summary
print("=== SUMMARY ===")
print("B2C headers:", len(b2c_headers))
print("B2C unique IDs:", len(set(b2c_ids)))
print("B2C dup IDs:", len(b2c_dups))
print("B2B headers:", len(b2b_headers))
print("B2B unique IDs:", len(set(b2b_ids)))
print("B2B dup IDs:", len(b2b_dups))
print("Common IDs between files:", sorted(common_ids, key=int))
print("Cross-file name matches:", len(cross_dups))
print("Written to:", out_file)
