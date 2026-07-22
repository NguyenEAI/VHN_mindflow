import json
with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
for node in data.get('sequence', []):
    if node.get('type') == 'recall':
        print(f"Recall node: {node.get('name')}, max_loop: {node.get('properties', {}).get('max_loop')}")
