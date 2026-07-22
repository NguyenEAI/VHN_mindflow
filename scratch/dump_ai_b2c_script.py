# -*- coding: utf-8 -*-
import json

def find_all_nodes(nodes, name, results):
    if not isinstance(nodes, list):
        return
    for n in nodes:
        if not isinstance(n, dict):
            continue
        if n.get('name') == name: 
            results.append(n)
        if 'branches' in n and isinstance(n['branches'], list):
            for b in n['branches']:
                if isinstance(b, dict):
                    find_all_nodes(b.get('sequence', []), name, results)

with open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', encoding='utf-8') as f:
    d = json.load(f)

results = []
find_all_nodes(d.get('sequence', []), 'AI Chuyên trách B2C', results)

if results:
    with open('c:/Users/Administrator/Desktop/Hoc_python/scratch/dump_ai_b2c.json', 'w', encoding='utf-8') as f:
        json.dump(results[0], f, indent=2, ensure_ascii=False)
    print('Found ' + str(len(results)))
else:
    print('Not found')
