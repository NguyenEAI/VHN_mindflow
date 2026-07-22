"""
FIX 4: Add URL verification step after B2C AI reply.
Adds a Python node that extracts URLs from bot_b2c_reply and checks
if they exist in knowledge_from_rag. If not, replaces them with a safe fallback.
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

def find_and_get_parent_list(obj, target_id, parent_list=None):
    """Find a node by ID and return (node, parent_list, index_in_list)."""
    if isinstance(obj, dict):
        for key, val in obj.items():
            if isinstance(val, list):
                for i, item in enumerate(val):
                    if isinstance(item, dict) and item.get("id") == target_id:
                        return (item, val, i)
                    result = find_and_get_parent_list(item, target_id, val)
                    if result:
                        return result
            elif isinstance(val, dict):
                result = find_and_get_parent_list(val, target_id)
                if result:
                    return result
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, dict) and item.get("id") == target_id:
                return (item, obj, i)
            result = find_and_get_parent_list(item, target_id, obj)
            if result:
                return result
    return None


# The Python verification code that will run after B2C reply
VERIFY_URL_CODE = r"""import re

reply = '''{{bot_b2c_reply}}'''
knowledge = '''{{knowledge_from_rag}}'''

# Extract all URLs from the reply
urls_in_reply = re.findall(r'https?://[^\s\)\]\"\']+', reply)

if urls_in_reply and knowledge.strip():
    # Extract all URLs from knowledge
    urls_in_knowledge = set(re.findall(r'https?://[^\s\)\]\"\']+', knowledge))
    
    # Check each URL in reply
    for url in urls_in_reply:
        # Clean trailing punctuation
        clean_url = url.rstrip('.,;:!?')
        if clean_url not in urls_in_knowledge:
            # URL not found in knowledge - likely hallucinated
            # Remove the entire line containing this URL
            lines = reply.split('\n')
            new_lines = []
            for line in lines:
                if clean_url in line or url in line:
                    # Skip this line (remove hallucinated URL)
                    pass
                else:
                    new_lines.append(line)
            reply = '\n'.join(new_lines)

# Clean up extra blank lines
while '\n\n\n' in reply:
    reply = reply.replace('\n\n\n', '\n\n')

output = reply
print(output)"""


def fix4_add_url_verify(data):
    print("=" * 60)
    print("FIX 4: Add URL verification step after B2C reply")
    print("=" * 60)
    
    # Find the B2C AI node to know where to insert after
    b2c_ai_id = None
    nodes = find_all(data, 'AI Chuyên trách B2C')
    if nodes:
        b2c_ai_id = nodes[0].get("id")
        print(f"  Found B2C AI node: id={b2c_ai_id}")
    else:
        print("  ERROR: Cannot find B2C AI node")
        return False
    
    # The verification node to insert
    verify_node = {
        "id": "b2c_url_verify",
        "type": "python",
        "componentType": "task",
        "name": "Verify URLs in B2C Reply",
        "properties": {
            "varName": "bot_b2c_reply",
            "expression": VERIFY_URL_CODE
        }
    }
    
    # Find the b2c_consult branch in the Flows Switch
    # We need to insert the verify_node right after the B2C AI node
    flow_switch = find_all(data, "Flows Switch")
    if not flow_switch:
        print("  ERROR: Cannot find Flows Switch")
        return False
    
    b2c_flow = flow_switch[0]["branches"]["b2c_consult"]
    
    # Find index of B2C AI in the b2c_consult list
    b2c_ai_idx = None
    for i, node in enumerate(b2c_flow):
        if node.get("id") == b2c_ai_id:
            b2c_ai_idx = i
            break
    
    if b2c_ai_idx is None:
        # The B2C AI might be nested (it's a direct child of b2c_consult)
        for i, node in enumerate(b2c_flow):
            if node.get("name") == "AI Chuyên trách B2C":
                b2c_ai_idx = i
                break
    
    if b2c_ai_idx is None:
        print("  ERROR: Cannot find B2C AI position in flow")
        print(f"  b2c_flow has {len(b2c_flow)} nodes:")
        for i, n in enumerate(b2c_flow):
            print(f"    [{i}] {n.get('name', 'unnamed')} (id={n.get('id', '?')})")
        return False
    
    # Check if verify node already exists
    for node in b2c_flow:
        if node.get("id") == "b2c_url_verify":
            print("  [SKIP] Verify node already exists")
            return True
    
    # Insert after B2C AI node
    b2c_flow.insert(b2c_ai_idx + 1, verify_node)
    print(f"  [OK] Inserted URL verify node at position {b2c_ai_idx + 1} (after B2C AI at {b2c_ai_idx})")
    
    # Also add for B2B
    b2b_flow = flow_switch[0]["branches"]["b2b_consult"]
    b2b_ai_idx = None
    for i, node in enumerate(b2b_flow):
        if node.get("name") == "AI Chuyên trách B2B":
            b2b_ai_idx = i
            break
    
    if b2b_ai_idx is not None:
        verify_node_b2b = {
            "id": "b2b_url_verify",
            "type": "python",
            "componentType": "task",
            "name": "Verify URLs in B2B Reply",
            "properties": {
                "varName": "bot_b2b_reply",
                "expression": VERIFY_URL_CODE.replace("bot_b2c_reply", "bot_b2b_reply")
            }
        }
        
        # Check if already exists
        exists = any(n.get("id") == "b2b_url_verify" for n in b2b_flow)
        if not exists:
            b2b_flow.insert(b2b_ai_idx + 1, verify_node_b2b)
            print(f"  [OK] Inserted URL verify node for B2B at position {b2b_ai_idx + 1}")
        else:
            print("  [SKIP] B2B verify node already exists")
    
    return True


if __name__ == "__main__":
    data = load()
    ok = fix4_add_url_verify(data)
    if ok:
        save(data)
        print("\nFIX 4 applied and saved successfully.")
    else:
        print("\nFIX 4 had issues.")
