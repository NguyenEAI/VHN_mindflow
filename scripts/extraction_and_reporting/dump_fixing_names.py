import json
import traceback

try:
    with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    names = []
    def get_names(seq):
        for node in seq:
            if 'name' in node: names.append(node['name'])
            if 'sequence' in node: get_names(node['sequence'])
            if 'branches' in node:
                for b in node['branches'].values(): get_names(b)

    get_names(data.get('sequence', []))
    with open('fixing_names.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(names))
    print("SUCCESS")
except Exception as e:
    with open('error_log2.txt', 'w') as f:
        f.write(traceback.format_exc())
    print("ERROR")
