import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def dump_recommend_branch(obj):
    if isinstance(obj, dict):
        if obj.get('name') == 'Recommend Product':
            for task in obj.get('sequence', []):
                t_type = task.get('type')
                t_name = task.get('name')
                print(f"Node Type: {t_type}, Name: {t_name}")
                if t_type == 'setVar':
                    print(f"  Sets: {task.get('properties', {}).get('varName', '')} to {task.get('properties', {}).get('varValue', '')[:200]}")
                elif t_type == 'llm':
                    print(f"  Model: {task.get('properties', {}).get('llm_alt_model', '')}")
            return True
        for k, v in obj.items():
            if dump_recommend_branch(v):
                return True
    elif isinstance(obj, list):
        for v in obj:
            if dump_recommend_branch(v):
                return True
    return False

dump_recommend_branch(data)
