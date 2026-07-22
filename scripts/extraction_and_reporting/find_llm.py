import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def find_llm_nodes(obj, current_node_name='Unknown'):
    if isinstance(obj, dict):
        if 'name' in obj:
            current_node_name = obj['name']
        if 'llm_alt_model' in obj:
            print(f"Found {obj['llm_alt_model']} at node: {current_node_name}")
        for k, v in obj.items():
            find_llm_nodes(v, current_node_name)
    elif isinstance(obj, list):
        for v in obj:
            find_llm_nodes(v, current_node_name)

find_llm_nodes(data)
