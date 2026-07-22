import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
def search_node(seq, path=[]):
    for i, node in enumerate(seq):
        if node.get('type') == 'botSendText':
            if '{{ order_info.reply_text }}' in str(node.get('properties', {}).get('text', '')):
                out.append(str(node.get('name')) + ' path: ' + str(path + [i]))
        if 'sequence' in node:
            search_node(node['sequence'], path + [i, 'sequence'])
        if 'branches' in node:
            for b_name, b_seq in node['branches'].items():
                search_node(b_seq, path + [i, 'branches', b_name])

search_node(data.get('sequence', []))
with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_all_reply.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
