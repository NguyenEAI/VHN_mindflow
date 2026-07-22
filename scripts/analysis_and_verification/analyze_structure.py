import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"--- Analysis of {file_path} ---")
    sequence = data.get('sequence', [])
    for idx, item in enumerate(sequence):
        print(f"[{idx}] {item.get('type', 'UNKNOWN')} - {item.get('name', 'Unnamed')}")
        if item.get('type') == 'flowSwitch':
            branches = item.get('branches', {})
            for branch_name, branch_tasks in branches.items():
                if branch_name in ['b2c_consult', 'b2b_consult']:
                    print(f"  Branch: {branch_name}")
                    for t_idx, t in enumerate(branch_tasks):
                        print(f"    [{t_idx}] {t.get('type', 'UNKNOWN')} - {t.get('name', 'Unnamed')}")

analyze_json(r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien.json')
print("\n")
analyze_json(r'c:\Users\Administrator\Desktop\Hoc_python\VHN_backup.json')
