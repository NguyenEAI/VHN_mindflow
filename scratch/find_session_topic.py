import json, re

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    text = f.read()

matches = re.finditer(r'session\.topic', text)
out = []
for m in matches:
    idx = m.start()
    out.append('Found session.topic at ' + str(idx))
    out.append(text[max(0, idx-100):min(len(text), idx+100)])

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\find_session_topic.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
