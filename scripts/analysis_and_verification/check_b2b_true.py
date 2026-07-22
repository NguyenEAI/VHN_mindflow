import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fs = next((n for n in data['sequence'] if n.get('type') == 'flowSwitch'), None)
if fs:
    b2b = fs['branches'].get('b2b_consult', [])
    last_node = b2b[-1]
    if last_node.get('type') == 'if':
        true_branch = last_node.get('branches', {}).get('true', [])
        print("Branches of If got lead (true branch):")
        print(json.dumps(true_branch, ensure_ascii=False, indent=2))
