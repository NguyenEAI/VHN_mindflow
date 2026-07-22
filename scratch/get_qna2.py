import json, codecs
with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
    d = json.load(f)

def get_qna_nodes(nodes):
    if not isinstance(nodes, list): return
    for n in nodes:
        if not isinstance(n, dict): continue
        typ = n.get('type')
        if typ == 'qna':
            name = n.get('name', '')
            inst = n.get('properties', {}).get('instruction', '')
            has_history = 'chat_history' in inst
            aware = n.get('properties', {}).get('chat_history_aware')
            with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/qna_nodes.txt', 'a', 'utf-8') as fw:
                fw.write(f'Node: {name} | has_history_in_prompt: {has_history} | chat_history_aware: {aware}\n')
        
        # Check inside flowSwitch branches
        if typ == 'flowSwitch':
            branches = n.get('properties', {}).get('branches', [])
            for b in branches:
                if isinstance(b, dict):
                    get_qna_nodes(b.get('sequence', []))
        
        # Check inside parallel branches
        if typ == 'parallel':
            branches = n.get('properties', {}).get('branches', [])
            for b in branches:
                if isinstance(b, dict):
                    get_qna_nodes(b.get('sequence', []))
                    
        # Check inside if branches
        if typ == 'if':
            branches = n.get('properties', {}).get('branches', {})
            get_qna_nodes(branches.get('true', []))
            get_qna_nodes(branches.get('false', []))

open('c:/Users/Administrator/Desktop/Hoc_python/scratch/qna_nodes.txt', 'w').close()

if isinstance(d, list):
    get_qna_nodes(d)
elif isinstance(d, dict) and 'sequence' in d:
    get_qna_nodes(d['sequence'])
else:
    with open('c:/Users/Administrator/Desktop/Hoc_python/scratch/qna_nodes.txt', 'w') as fw:
        fw.write("Unknown root format\n")
