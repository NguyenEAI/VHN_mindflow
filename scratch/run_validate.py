import json, codecs, re, sys
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

data = json.load(codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8'))
text = json.dumps(data, ensure_ascii=False)

# 1. Top-level flowSwitch
fs_top = sum(1 for b in data.get('sequence', []) if b.get('type') == 'flowSwitch')
print(f"[1] Top-level flowSwitch: {fs_top} {'OK' if fs_top == 1 else 'SAI!'}")

# 2. Complex conditions
complex_conds = re.findall(r'"condition":\s*"[^"]*(?:!=|\sand\s|\()[^"]*"', text)
print(f"[2] Complex conditions: {len(complex_conds)} {'OK' if len(complex_conds) == 0 else 'SAI!'}")
for c in complex_conds: print(f"  → {c}")

# 3. Templated conditions
templated_conds = re.findall(r'"condition":\s*"[^"]*\{\{[^"]*"', text)
print(f"[3] Templated conditions: {len(templated_conds)} {'OK' if len(templated_conds) == 0 else 'SAI!'}")
for c in templated_conds: print(f"  → {c}")

# 4. setTopic components
set_topics = re.findall(r'"type":\s*"setTopic"', text)
print(f"[4] setTopic components: {len(set_topics)} {'OK' if len(set_topics) == 0 else 'SAI!'}")

# 5. parallel components
parallels = re.findall(r'"type":\s*"parallel"', text)
print(f"[5] parallel components: {len(parallels)} {'OK if intended for true parallel exec' if len(parallels) == 0 else 'CHECK!'}")

# 6. recall properties
recall_with_props = re.findall(r'"type":\s*"recall"[^}]*"properties":\s*\{[^}]+\}', text)
print(f"[6] recall with non-empty properties: {len(recall_with_props)} {'OK' if len(recall_with_props) == 0 else 'SAI!'}")

# 7. botSendText with {{#if}}
botsend_with_if = re.findall(r'"botSendText"[^}]*"text":\s*"[^"]*\{\{#if', text)
print(f"[8] botSendText with {{{{#if}}}}: {len(botsend_with_if)} {'OK' if len(botsend_with_if) == 0 else 'SAI!'}")
