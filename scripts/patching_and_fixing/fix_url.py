import json

file_path = r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

product_sheet_url = "https://docs.google.com/spreadsheets/d/1LdO_BV7DHdgs0_GAqTTkQbWkwefUQqw036Cb3PJcUJM/edit?usp=sharing"

fs = next((n for n in data['sequence'] if n.get('type') == 'flowSwitch'), None)
if fs:
    for branch_name in ['b2c_consult', 'b2b_consult']:
        branch_tasks = fs['branches'][branch_name]
        for task in branch_tasks:
            # We are looking for the 'If need product info' node
            if task.get('name') == 'If need product info':
                true_branch = task['branches']['true']
                for subtask in true_branch:
                    if subtask.get('type') == 'botAPICall' and subtask.get('name') == 'API CALL PRODUCT DATA':
                        api_body = subtask['properties']['api_body']
                        # Replace {{ sheet_url }} with the correct hardcoded product sheet URL
                        if "{{ sheet_url }}" in api_body:
                            subtask['properties']['api_body'] = api_body.replace("{{ sheet_url }}", product_sheet_url)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    
print("Successfully fixed product sheet URL in VHN_DauTien_Fixed.json")
