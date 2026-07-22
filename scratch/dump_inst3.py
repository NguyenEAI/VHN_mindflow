import json, codecs
try:
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
        d = json.load(f)
        
    out = []
    
    def dump_all_inst(nodes):
        if not isinstance(nodes, list): return
        for n in nodes:
            if not isinstance(n, dict): continue
            
            name = n.get('name', 'UNKNOWN')
            if n.get('type') == 'qna':
                inst = n.get('properties', {}).get('instruction', '')
                out.append(f"====== NODE: {name} ======")
                out.append(inst[:200] + "\n...")
                out.append(f"chat_history_aware: {n.get('properties', {}).get('chat_history_aware')}")
                out.append("")
                
            if 'sequence' in n:
                dump_all_inst(n['sequence'])
                
            if 'branches' in n.get('properties', {}):
                branches = n.get('properties', {}).get('branches')
                if isinstance(branches, list):
                    for b in branches:
                        if isinstance(b, dict):
                            dump_all_inst(b.get('sequence', []))
                elif isinstance(branches, dict):
                    dump_all_inst(branches.get('true', []))
                    dump_all_inst(branches.get('false', []))
                    
            if n.get('type') == 'flowSwitch':
                for k, v in n.items():
                    if isinstance(v, list):
                        dump_all_inst(v)
                        
    dump_all_inst(d.get('sequence', []))
    
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/all_qna_inst.txt', 'w', 'utf-8') as fw:
        fw.write("\n".join(out))
except Exception as e:
    with open('c:/Users/Administrator/Desktop/Hoc_python/scratch/all_qna_inst.txt', 'w') as fw:
        fw.write(f'Error: {e}')
