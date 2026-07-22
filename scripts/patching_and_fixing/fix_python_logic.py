import json

with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

new_python_code = r"""import json

MANAGER = r\"\"\"{{sales_manager}}\"\"\"
MANAGER = MANAGER.strip()
if MANAGER.startswith("```json"):
    MANAGER = MANAGER[7:]
elif MANAGER.startswith("```"):
    MANAGER = MANAGER[3:]
if MANAGER.endswith("```"):
    MANAGER = MANAGER[:-3]
MANAGER = MANAGER.strip()

PHASES = ["greetings", "qna", "agency_gather_info", "gather_requirement", "recommend_product", "handover", "off_topic", "thank_you"]

if type(MANAGER).__name__ == 'str':
    try:
        parsed_data = json.loads(MANAGER)
        
        phase_value = parsed_data.get("phase", "") or ""
        
        if phase_value in PHASES:
            print("Yes")
        else:
            # If phase is missing or invalid, we recall
            print("No")
    except Exception as e:
        print("No")
else:
    print("No")"""

for node in data.get('sequence', []):
    if node.get('type') == 'block':
        for task in node.get('sequence', []):
            if task.get('name') == 'Python':
                if 'verify_manager_decision_format' in task.get('properties', {}).get('varName', ''):
                    task['properties']['expression'] = new_python_code
                    print("Updated Python node for manager decision format!")

with open('VHN_fixing.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
