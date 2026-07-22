import json

with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

new_python_code = """import json

MANAGER = \"\"\"{{sales_manager}}\"\"\"
MANAGER = MANAGER.strip()
if MANAGER.startswith("```json"):
    MANAGER = MANAGER[7:]
elif MANAGER.startswith("```"):
    MANAGER = MANAGER[3:]
if MANAGER.endswith("```"):
    MANAGER = MANAGER[:-3]
MANAGER = MANAGER.strip()

KEYS = ["phase", "need_product_info", "customer_class", "current_step", "customer_name", "customer_phone", "user_context", "target_product", "note_for_sales"]
PHASES = ["greetings", "qna", "agency_gather_info", "gather_requirement", "recommend_product", "handover", "off_topic", "thank_you"]
NOTES = ["none", "spa", "clinic", "aesthetic", "hospital", "pharmacy"]
CLASS = ["agency", "retail", "personal"]

if type(MANAGER).__name__ == 'str':
    try:
        parsed_data = json.loads(MANAGER)
        
        # Always output valid phase, note, class even if missing/null to prevent crash
        phase_value = parsed_data.get("phase", "") or ""
        note_value = parsed_data.get("note_for_sales", "") or ""
        class_value = parsed_data.get("customer_class", "") or ""

        result_phase = any(key in phase_value for key in PHASES)
        result_note = any(key in note_value for key in NOTES)
        result_class = any(key in class_value for key in CLASS)

        missing_keys = [k for k in KEYS if k not in parsed_data]

        if not missing_keys and result_phase and result_note and result_class:
            print("Yes")
        else:
            print("No")
    except json.JSONDecodeError:
        print("No")
    except Exception as e:
        print("No")
else:
    print("No")"""

for node in data.get('sequence', []):
    if node.get('type') == 'block':
        for task in node.get('sequence', []):
            if task.get('name') == 'Python':
                task['properties']['expression'] = new_python_code
                print("Updated Python node inside block!")

with open('VHN_fixing.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
