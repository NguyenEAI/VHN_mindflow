"""
FIX 5: Reduce Knowledge Result Limit from 7 to 5 for B2C and B2B.
"""
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

INPUT_FILE = r"c:\Users\Administrator\Desktop\Hoc_python\ai_fixed.txt"

def load():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save(data):
    with open(INPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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

def fix5_reduce_limit(data):
    print("=" * 60)
    print("FIX 5: Reduce Knowledge Result Limit")
    print("=" * 60)
    
    targets = [
        ("AI Chuyên trách B2C", "7", "5"),
        ("AI Chuyên trách B2B", "7", "5"),
    ]
    
    for name, old_limit, new_limit in targets:
        nodes = find_all(data, name)
        if not nodes:
            print(f"  [WARN] Cannot find '{name}'")
            continue
        
        current = nodes[0]["properties"].get("limit", "N/A")
        if current == old_limit:
            nodes[0]["properties"]["limit"] = new_limit
            print(f"  [OK] {name}: limit {old_limit} → {new_limit}")
        elif current == new_limit:
            print(f"  [SKIP] {name}: already at {new_limit}")
        else:
            print(f"  [INFO] {name}: current limit is '{current}', setting to {new_limit}")
            nodes[0]["properties"]["limit"] = new_limit
    
    return True


if __name__ == "__main__":
    data = load()
    ok = fix5_reduce_limit(data)
    if ok:
        save(data)
        print("\nFIX 5 applied and saved successfully.")
    
    # Quick verify
    data2 = load()
    for name in ["AI Chuyên trách B2C", "AI Chuyên trách B2B"]:
        nodes = find_all(data2, name)
        limit = nodes[0]["properties"].get("limit", "N/A")
        status = "PASS" if limit == "5" else "FAIL"
        print(f"  [{status}] {name}: limit = {limit}")
