import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
def search_node(seq, path=[]):
    for i, node in enumerate(seq):
        if node.get('name') == 'Set topic':
            out.append('Found Set topic at path: ' + str(path + [i]))
            if i > 0:
                out.append('Previous node: ' + str(seq[i-1].get('name')) + ' properties: ' + str(seq[i-1].get('properties')))
            else:
                out.append('It is the first node in the sequence!')
        if 'sequence' in node:
            search_node(node['sequence'], path + [i, 'sequence'])
        if 'branches' in node:
            for b_name, b_seq in node['branches'].items():
                search_node(b_seq, path + [i, 'branches', b_name])

search_node(data.get('sequence', []))
with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\count_set_topic.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
