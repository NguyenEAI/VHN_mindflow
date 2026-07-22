import json

file_path = r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

fs = next((n for n in data['sequence'] if n.get('type') == 'flowSwitch'), None)
if fs:
    b2b_consult = fs['branches'].get('b2b_consult', [])
    # Find "If got lead"
    for task in b2b_consult:
        if task.get('name') == 'If got lead' and task.get('type') == 'if':
            false_branch_lead = task.get('branches', {}).get('false', [])
            if false_branch_lead:
                if_exit = false_branch_lead[0]
                if if_exit.get('name') == 'If exit':
                    # Add botSendText to false branch of if_exit
                    false_branch_exit = if_exit.get('branches', {}).get('false', [])
                    if len(false_branch_exit) == 0:
                        bot_send = {
                            "id": "b2b_send_reply_fixed",
                            "type": "botSendText",
                            "componentType": "task",
                            "properties": {
                                "text": "{{ bot_b2b_reply }}"
                            },
                            "name": "Bot Send B2B Reply"
                        }
                        if_exit['branches']['false'].append(bot_send)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Added missing botSendText to b2b_consult.")
