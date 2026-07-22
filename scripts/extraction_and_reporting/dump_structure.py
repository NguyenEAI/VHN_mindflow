import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def dump_structure(obj, indent=''):
    if isinstance(obj, dict):
        if 'name' in obj:
            print(f"{indent}Node: {obj['name']} ({obj.get('type')})")
            if obj.get('type') == 'setVar':
                print(f"{indent}  Var: {obj.get('properties', {}).get('varName', '')}")
            if obj.get('type') == 'botAPICall':
                print(f"{indent}  URL: {obj.get('properties', {}).get('api_url', '')}")
            if obj.get('type') == 'llm':
                instr = obj.get('properties', {}).get('instruction', '')
                print(f"{indent}  Prompt length: {len(instr)}")
        for k, v in obj.items():
            if k == 'sequence' or k == 'conditions' or k == 'branches':
                if isinstance(v, list):
                    for item in v:
                        dump_structure(item, indent + '  ')
                elif isinstance(v, dict):
                    for branch_name, branch_content in v.items():
                        print(f"{indent}  Branch: {branch_name}")
                        dump_structure(branch_content, indent + '    ')
            else:
                dump_structure(v, indent)
    elif isinstance(obj, list):
        for item in obj:
            dump_structure(item, indent)

dump_structure(data)
