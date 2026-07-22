import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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

def print_matches(file_path, keyword):
    print(f"--- Matches for '{keyword}' in {file_path} ---")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        matches = search_json(data, keyword)
        for m in matches:
            print(f"Path: {m[0]}")
            val = m[2]
            if len(val) > 200: val = val[:100] + "..." + val[-100:]
            print(f"Match: {val}")
    except Exception as e:
        print(f"Error: {e}")

print_matches(r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien.json', r'sheet|http|url')
print_matches(r'c:\Users\Administrator\Desktop\Hoc_python\VHN_backup.json', r'sheet|http|url')
