import json
import codecs

try:
    file_path = 'c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json'
    with codecs.open(file_path, 'r', 'utf-8') as f:
        d = json.load(f)

    patched_b2c = False
    patched_b2b = False

    def patch_node(nodes):
        global patched_b2c, patched_b2b
        if not isinstance(nodes, list): return
        for n in nodes:
            if not isinstance(n, dict): continue
            
            if n.get('name') == 'Collect chat_history_b2c':
                if 'varName' not in n.get('properties', {}):
                    n['properties']['varName'] = 'session.extra.chat_history_b2c'
                    patched_b2c = True
            
            elif n.get('name') == 'Collect chat_history_b2b':
                if 'varName' not in n.get('properties', {}):
                    n['properties']['varName'] = 'session.extra.chat_history_b2b'
                    patched_b2b = True
                
            if 'sequence' in n:
                patch_node(n['sequence'])
                
            if 'branches' in n:
                branches = n['branches']
                if isinstance(branches, list):
                    for b in branches:
                        if isinstance(b, dict):
                            patch_node(b.get('sequence', []))
                elif isinstance(branches, dict):
                    for k, v in branches.items():
                        if isinstance(v, list):
                            patch_node(v)
                        elif isinstance(v, dict):
                            patch_node(v.get('sequence', []))
                            
            if 'branches' in n.get('properties', {}):
                branches = n['properties']['branches']
                if isinstance(branches, list):
                    for b in branches:
                        if isinstance(b, dict):
                            patch_node(b.get('sequence', []))
                elif isinstance(branches, dict):
                    for k, v in branches.items():
                        if isinstance(v, list):
                            patch_node(v)
                        elif isinstance(v, dict):
                            patch_node(v.get('sequence', []))

    patch_node(d.get('sequence', []))

    if patched_b2c or patched_b2b:
        with codecs.open(file_path, 'w', 'utf-8') as fw:
            json.dump(d, fw, ensure_ascii=False, indent=2)
        print("Patched successfully!")
        print("patched_b2c:", patched_b2c)
        print("patched_b2b:", patched_b2b)
    else:
        print("Could not find or already patched")

except Exception as e:
    print("Error:", e)
