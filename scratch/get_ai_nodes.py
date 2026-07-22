import json
import codecs

with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
    d = json.load(f)

def get_ai_nodes(nodes):
    if not isinstance(nodes, list): return
    for n in nodes:
        if not isinstance(n, dict): continue
        name = n.get('name', '')
        if 'AI ' in name:
            inst = n.get('properties', {}).get('instruction', '')
            has_history = 'chat_history' in inst
            aware = n.get('properties', {}).get('chat_history_aware')
            with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/ai_nodes.txt', 'a', 'utf-8') as fw:
                fw.write(f"Node: {name} | has_history_in_prompt: {has_history} | chat_history_aware: {aware}\n")
        if 'branches' in n and isinstance(n['branches'], list):
            for b in n['branches']:
                if isinstance(b, dict):
                    get_ai_nodes(b.get('sequence', []))

open('c:/Users/Administrator/Desktop/Hoc_python/scratch/ai_nodes.txt', 'w').close()
get_ai_nodes(d.get('sequence', []))
