import json
import traceback

try:
    with open('VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    nodes = []
    def find_node(seq, name):
        for node in seq:
            if node.get('name') == name:
                nodes.append(node)
            if 'sequence' in node:
                find_node(node['sequence'], name)
            if 'branches' in node:
                for b in node['branches'].values():
                    find_node(b, name)

    find_node(data.get('sequence', []), 'API CALL PRODUCT DATA')
    
    with open('dump_api_call.json', 'w', encoding='utf-8') as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)
    print("SUCCESS")
except Exception as e:
    with open('error_log.txt', 'w') as f:
        f.write(traceback.format_exc())
    print("ERROR")
