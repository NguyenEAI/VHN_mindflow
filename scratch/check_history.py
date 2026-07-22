import json
import codecs

with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
    d = json.load(f)

def check_history(nodes):
    if not isinstance(nodes, list): return
    for n in nodes:
        if not isinstance(n, dict): continue
        if 'AI Chuyên trách' in n.get('name', ''):
            inst = n.get('properties', {}).get('instruction', '')
            has_history = 'chat_history' in inst
            aware = n.get('properties', {}).get('chat_history_aware')
            with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/history_check.txt', 'a', 'utf-8') as fw:
                fw.write(f"{n.get('name')} - Has chat_history in prompt: {has_history} - chat_history_aware: {aware}\n")
        if 'branches' in n and isinstance(n['branches'], list):
            for b in n['branches']:
                if isinstance(b, dict):
                    check_history(b.get('sequence', []))

open('c:/Users/Administrator/Desktop/Hoc_python/scratch/history_check.txt', 'w').close()
check_history(d.get('sequence', []))
