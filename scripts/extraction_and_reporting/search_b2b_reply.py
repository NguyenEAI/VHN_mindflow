import json
import re

def search_json(obj, keyword, path=""):
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_path = f"{path}.{k}" if path else k
            if isinstance(k, str) and re.search(keyword, k, re.IGNORECASE):
                results.append((new_path, "KEY_MATCH", k))
            results.extend(search_json(v, keyword, new_path))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_path = f"{path}[{i}]"
            results.extend(search_json(v, keyword, new_path))
    elif isinstance(obj, str):
        if re.search(keyword, obj, re.IGNORECASE):
            results.append((path, "VALUE_MATCH", obj))
    return results

with open(r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
matches = search_json(data, 'bot_b2b_reply')
for m in matches:
    print(f"Path: {m[0]}")
