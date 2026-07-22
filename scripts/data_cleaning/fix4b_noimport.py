"""
FIX 4b: Rewrite URL verification WITHOUT import re.
Uses pure string operations only (no imports).
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

# New verification code - NO IMPORTS at all
VERIFY_URL_CODE_B2C = r"""reply = '''{{bot_b2c_reply}}'''
knowledge = '''{{knowledge_from_rag}}'''

def extract_urls(text):
    urls = []
    i = 0
    while i < len(text):
        start = -1
        if text[i:i+8] == 'https://':
            start = i
        elif text[i:i+7] == 'http://':
            start = i
        if start >= 0:
            end = start
            while end < len(text) and text[end] not in ' \n\r\t)]\"\'>':
                end = end + 1
            url = text[start:end].rstrip('.,;:!?')
            if len(url) > 10:
                urls.append(url)
            i = end
        else:
            i = i + 1
    return urls

urls_in_reply = extract_urls(reply)

if len(urls_in_reply) > 0 and len(knowledge.strip()) > 0:
    urls_in_knowledge = extract_urls(knowledge)
    knowledge_url_set = {}
    for u in urls_in_knowledge:
        knowledge_url_set[u] = True

    for url in urls_in_reply:
        if url not in knowledge_url_set:
            lines = reply.split('\n')
            new_lines = []
            for line in lines:
                if url not in line:
                    new_lines.append(line)
            reply = '\n'.join(new_lines)

while '\n\n\n' in reply:
    reply = reply.replace('\n\n\n', '\n\n')

output = reply
print(output)"""

VERIFY_URL_CODE_B2B = VERIFY_URL_CODE_B2C.replace("bot_b2c_reply", "bot_b2b_reply")


def fix4b_rewrite_verify(data):
    print("=" * 60)
    print("FIX 4b: Rewrite URL verify WITHOUT import re")
    print("=" * 60)
    
    flow_switch = find_all(data, "Flows Switch")
    if not flow_switch:
        print("  ERROR: Cannot find Flows Switch")
        return False
    
    # Update B2C verify node
    b2c_flow = flow_switch[0]["branches"]["b2c_consult"]
    for node in b2c_flow:
        if node.get("id") == "b2c_url_verify":
            old_code = node["properties"]["expression"]
            has_import = "import re" in old_code
            node["properties"]["expression"] = VERIFY_URL_CODE_B2C
            print(f"  [OK] Updated B2C verify node (had 'import re': {has_import})")
            break
    else:
        print("  [WARN] B2C verify node not found")
    
    # Update B2B verify node
    b2b_flow = flow_switch[0]["branches"]["b2b_consult"]
    for node in b2b_flow:
        if node.get("id") == "b2b_url_verify":
            old_code = node["properties"]["expression"]
            has_import = "import re" in old_code
            node["properties"]["expression"] = VERIFY_URL_CODE_B2B
            print(f"  [OK] Updated B2B verify node (had 'import re': {has_import})")
            break
    else:
        print("  [WARN] B2B verify node not found")
    
    return True


def verify(data):
    print("\n--- Verification ---")
    flow_switch = find_all(data, "Flows Switch")
    
    for flow_name, verify_id in [("b2c_consult", "b2c_url_verify"), ("b2b_consult", "b2b_url_verify")]:
        flow = flow_switch[0]["branches"][flow_name]
        for node in flow:
            if node.get("id") == verify_id:
                code = node["properties"]["expression"]
                has_import = "import " in code
                has_extract = "extract_urls" in code
                has_knowledge = "knowledge" in code
                print(f"  [{flow_name}]")
                print(f"    [{'FAIL' if has_import else 'PASS'}] No imports")
                print(f"    [{'PASS' if has_extract else 'FAIL'}] Has extract_urls function")
                print(f"    [{'PASS' if has_knowledge else 'FAIL'}] Checks against knowledge")
                print(f"    Code length: {len(code)} chars")
                break


if __name__ == "__main__":
    data = load()
    ok = fix4b_rewrite_verify(data)
    if ok:
        save(data)
        print("\nFIX 4b applied and saved.")
    
    data2 = load()
    verify(data2)
