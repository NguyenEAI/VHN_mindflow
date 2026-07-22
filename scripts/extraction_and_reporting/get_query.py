import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
def get_node_instruction(obj, target_name):
    if isinstance(obj, dict):
        if obj.get('name') == target_name:
            print(f"--- {target_name} ---")
            print(obj.get('properties', {}).get('instruction', 'No instruction')[:1500])
            return True
        for k, v in obj.items():
            if get_node_instruction(v, target_name):
                return True
    elif isinstance(obj, list):
        for v in obj:
            if get_node_instruction(v, target_name):
                return True
    return False
get_node_instruction(data, 'GPT-4 Query Data')
get_node_instruction(data, 'GPT-4 Analysis')
