import json, codecs
try:
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
        d = json.load(f)

    all_names = []
    
    def extract_names(nodes):
        if not isinstance(nodes, list): return
        for n in nodes:
            if not isinstance(n, dict): continue
            
            name = n.get('name', 'UNKNOWN')
            typ = n.get('type', 'UNKNOWN')
            
            if typ == 'qna':
                inst = n.get('properties', {}).get('instruction', '')
                has_history = 'chat_history' in inst
                aware = n.get('properties', {}).get('chat_history_aware')
                all_names.append(f"QNA: {name} | history_in_prompt: {has_history} | chat_history_aware: {aware}")
            else:
                all_names.append(f"{typ}: {name}")
                
            if 'sequence' in n:
                extract_names(n['sequence'])
                
            if 'branches' in n.get('properties', {}):
                branches = n.get('properties', {}).get('branches')
                if isinstance(branches, list):
                    for b in branches:
                        if isinstance(b, dict):
                            extract_names(b.get('sequence', []))
                elif isinstance(branches, dict):
                    extract_names(branches.get('true', []))
                    extract_names(branches.get('false', []))
                    
    extract_names(d.get('sequence', []))
    
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/all_names.txt', 'w', 'utf-8') as fw:
        fw.write('\n'.join(all_names))
except Exception as e:
    with open('c:/Users/Administrator/Desktop/Hoc_python/scratch/all_names.txt', 'w') as fw:
        fw.write(f"Error: {e}\n")
