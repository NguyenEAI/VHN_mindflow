import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
def search_node(seq):
    for node in seq:
        if node.get('type') == 'botSendText':
            if '{{ order_info.reply_text }}' in str(node.get('properties', {}).get('text', '')):
                out.append('Found botSendText: ' + str(node.get('name')))
        if 'sequence' in node:
            search_node(node['sequence'])
        if 'branches' in node:
            for b in node['branches'].values():
                search_node(b)

search_node(data.get('sequence', []))
with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_botsendtext.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
