import json
with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def get_node(obj, target_name):
    if isinstance(obj, dict):
        if obj.get('name') == target_name:
            with open('manager_output.txt', 'w', encoding='utf-8') as out:
                out.write(obj.get('properties', {}).get('instruction', 'No instruction')[:1500])
            return True
        for k, v in obj.items():
            if get_node(v, target_name):
                return True
    elif isinstance(obj, list):
        for v in obj:
            if get_node(v, target_name):
                return True
    return False

get_node(data, 'GPT-4 MANAGER')
