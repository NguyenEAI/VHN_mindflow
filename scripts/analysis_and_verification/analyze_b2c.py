import json
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('ai_fixed.txt', 'r', encoding='utf-8') as f:
    data = json.load(f)

def find_all(obj, target_name):
    results = []
    if isinstance(obj, dict):
        if obj.get('name') == target_name:
            results.append(obj)
        for v in obj.values():
            results.extend(find_all(v, target_name))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(find_all(item, target_name))
    return results

# Extract B2C instruction
nodes = find_all(data, 'AI Chuyên trách B2C')
inst = nodes[0]['properties']['instruction']

# Find all blocks related to link/image rules
patterns = [
    "QUY TẮC SẮT",
    "LINK & HÌNH ẢNH",
    "LINK SẢN PHẨM",
    "KHÔNG HALLUCINATE",
    "VÍ DỤ VI PHẠM",
    "VÍ DỤ SAI",
    "NGUYÊN TẮC CHUNG",
    "TUYỆT ĐỐI KHÔNG bịa URL",
    "KHÔNG bịa link",
    "Quy tắc NGHIÊM NGẶT",
    "QUY TẮC TUYỆT ĐỐI VỀ LINK",
    "QUY TẮC BẮT BUỘC VỚI LINK",
    "QUY TẮC ĐỊNH DẠNG OUTPUT",
    "QUY TẮC BẮT BUỘC VỀ TÊN SẢN PHẨM",
]

print("=== ANALYZING DUPLICATE LINK/IMAGE RULES IN B2C ===\n")

# Split instruction into sections by finding ## or # headings (lines starting with #)
lines = inst.split('\n')
sections = []
current_section = {"title": "(intro)", "start": 0, "lines": []}

for i, line in enumerate(lines):
    if line.startswith('#') or line.startswith('## ') or line.startswith('### '):
        if current_section["lines"]:
            sections.append(current_section)
        current_section = {"title": line.strip(), "start": i, "lines": [line]}
    else:
        current_section["lines"].append(line)

if current_section["lines"]:
    sections.append(current_section)

print(f"Total sections: {len(sections)}\n")

# Find sections mentioning link/image/URL/bịa
link_related = []
for sec in sections:
    content = '\n'.join(sec["lines"])
    title = sec["title"]
    keywords_found = []
    for kw in ["link", "URL", "ảnh", "bịa", "HALLUCINATE", "Hình ảnh", "Link sản phẩm", "anchor text", "placeholder"]:
        if kw.lower() in content.lower():
            keywords_found.append(kw)
    if keywords_found:
        link_related.append((title, len(content), keywords_found))

print("=== SECTIONS MENTIONING LINK/IMAGE/URL/BIA ===")
for i, (title, length, kws) in enumerate(link_related, 1):
    print(f"\n{i}. [{length} chars] {title}")
    print(f"   Keywords: {', '.join(kws)}")

# Count total chars in link/image related sections
total_link_chars = sum(l for _,l,_ in link_related)
print(f"\nTotal link/image related content: {total_link_chars} chars out of {len(inst)} total ({100*total_link_chars//len(inst)}%)")
