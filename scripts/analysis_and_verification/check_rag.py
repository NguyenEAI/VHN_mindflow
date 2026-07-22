import json
with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def check_rag(obj):
    if isinstance(obj, dict):
        if obj.get('name') and (obj.get('type') == 'qna' or obj.get('type') == 'chat'):
            name = obj.get('name')
            props = obj.get('properties', {})
            aware = props.get('knowledge_aware', False)
            print(f"Node: {name} | knowledge_aware: {aware}")
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                check_rag(v)
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, (dict, list)):
                check_rag(v)

check_rag(data)
