import json

with open('VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

prompts = {}

def find_prompts(seq):
    for node in seq:
        if node.get('type') == 'qna' and 'instruction' in node.get('properties', {}):
            prompts[node['name']] = node['properties']['instruction']
        if 'sequence' in node:
            find_prompts(node['sequence'])
        if 'branches' in node:
            for b in node['branches'].values():
                find_prompts(b)

find_prompts(data.get('sequence', []))

with open('all_prompts.json', 'w', encoding='utf-8') as f:
    json.dump(prompts, f, ensure_ascii=False, indent=2)
