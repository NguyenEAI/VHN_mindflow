import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def find_recommend_branch(obj):
    if isinstance(obj, dict):
        if obj.get('name') == 'Recommend Product':
            print('Found Recommend Product phase block')
            for task in obj.get('sequence', []):
                t_type = task.get('type')
                t_name = task.get('name')
                props = task.get('properties', {})
                var = props.get('varName', props.get('varReply', ''))
                print(f"- {t_type}: {t_name} (var: {var})")
                
                # If this is the API node, print its instruction/URL
                if t_type == 'api':
                    print(f"  URL: {props.get('url', '')}")
                    
                # If this is an LLM node, print its model and prompt length
                if t_type == 'llm':
                    instr = props.get('instruction', '')
                    print(f"  Model: {props.get('llm_alt_model', '')}, Prompt length: {len(instr)} chars")
            return True
        for k, v in obj.items():
            if find_recommend_branch(v):
                return True
    elif isinstance(obj, list):
        for v in obj:
            if find_recommend_branch(v):
                return True
    return False

find_recommend_branch(data)
