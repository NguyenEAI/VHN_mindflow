import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

sequence = data.get('sequence', [])
for idx, item in enumerate(sequence):
    if item.get('type') == 'flowSwitch':
        branches = item.get('branches', {})
        for branch_name, branch_tasks in branches.items():
            if branch_name == 'b2c_consult':
                print(f"--- b2c_consult ---")
                print(json.dumps(branch_tasks, indent=2, ensure_ascii=False))
