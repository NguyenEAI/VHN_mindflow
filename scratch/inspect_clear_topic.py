import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
def search_node(seq):
    for node in seq:
        if node.get('name') == 'Clear Topic':
            out.append('Type: ' + str(node.get('type')))
            out.append('ComponentType: ' + str(node.get('componentType')))
            if 'properties' in node:
                out.append('Properties: ' + str(node['properties']))
            return True
        if 'sequence' in node:
            if search_node(node['sequence']): return True
        if 'branches' in node:
            for b in node['branches'].values():
                if search_node(b): return True
    return False

search_node(data.get('sequence', []))
with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_clear_topic.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
