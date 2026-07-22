import json, re
d = json.load(open('VHN_fixing.json', encoding='utf-8'))
t = json.dumps(d, ensure_ascii=False)
# Find all condition values
for m in re.finditer(r'"condition"\s*:\s*"(.*?)"', t):
    print(f"  {m.group(1)}")
