import json
import re

with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for node in data.get('sequence', []):
    if node.get('type') == 'block':
        for task in node.get('sequence', []):
            if task.get('name') == 'GPT-4 MANAGER':
                inst = task['properties']['instruction']
                inst = inst.replace("## phase\n## phase", "## phase")
                inst = inst.replace("# CONSTRAINTS\n# CONSTRAINTS", "# CONSTRAINTS")
                task['properties']['instruction'] = inst
                print("Fixed double headings in GPT-4 MANAGER")

with open('VHN_fixing.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
