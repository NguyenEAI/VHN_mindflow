import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fs = next((n for n in data['sequence'] if n.get('type') == 'flowSwitch'), None)
if fs:
    b2b = fs['branches'].get('b2b_consult', [])
    print("--- b2b_consult in VHN_DauTien.json ---")
    for i, t in enumerate(b2b):
        print(f"[{i}] {t.get('type')} - {t.get('name')}")
        
    print("\nLet's check if the last node in if_got_lead has botSendText")
    last_node = b2b[-1]
    if last_node.get('type') == 'if':
        false_branch = last_node.get('branches', {}).get('false', [])
        print("False branch of If got lead:")
        for i, t in enumerate(false_branch):
            print(f"[{i}] {t.get('type')} - {t.get('name')}")
