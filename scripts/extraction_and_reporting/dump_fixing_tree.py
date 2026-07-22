import json
with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
out = ""
def print_names(seq, indent=0):
    global out
    for node in seq:
        out += ' ' * indent + node.get('name', str(node.get('type'))) + '\n'
        if 'sequence' in node:
            print_names(node['sequence'], indent + 2)
        if 'branches' in node:
            for b in node['branches'].values():
                print_names(b, indent + 2)
print_names(data.get('sequence', []))
with open('dump_fixing_tree.txt', 'w', encoding='utf-8') as f:
    f.write(out)
