import json, codecs

# Load the file
with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
    data = json.load(f)

def fix_nodes(nodes):
    if not isinstance(nodes, list): return False
    changed = False
    
    for i, n in enumerate(nodes):
        if not isinstance(n, dict): continue
        
        # Replace setTopic with botSendText
        if n.get('type') == 'setTopic':
            n['type'] = 'botSendText'
            n['name'] = 'Bot Send Text - Proceed to Order'
            n['properties'] = {
                "text": "Dạ vâng, để em tiến hành hỗ trợ Anh/Chị đặt hàng nhé. Anh/Chị vui lòng xác nhận giúp em ạ."
            }
            changed = True
            print("Fixed setTopic")
            
        # Replace recall with clearTopic
        elif n.get('type') == 'recall':
            n['type'] = 'clearTopic'
            n['name'] = 'Clear Topic'
            n['properties'] = {}
            changed = True
            print("Fixed recall")
            
        if 'sequence' in n:
            if fix_nodes(n['sequence']): changed = True
            
        if 'branches' in n:
            b = n['branches']
            if isinstance(b, dict):
                for v in b.values():
                    if isinstance(v, list):
                        if fix_nodes(v): changed = True
                        
    return changed

if fix_nodes(data.get('sequence', [])):
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'w', 'utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Fixed and saved VHN_DauTien_Fixed.json")
else:
    print("No changes made.")
