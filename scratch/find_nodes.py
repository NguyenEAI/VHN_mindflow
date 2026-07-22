import json
import codecs
try:
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
        d = json.load(f)
    found = []
    def chk(nodes):
        if not isinstance(nodes, list): return
        for n in nodes:
            if not isinstance(n, dict): continue
            name = n.get('name', '')
            if name.startswith('Collect chat_history'):
                found.append(n)
            if 'sequence' in n: chk(n['sequence'])
            if 'branches' in n:
                b = n['branches']
                if isinstance(b, list):
                    for x in b:
                        if isinstance(x, dict): chk(x.get('sequence', []))
                elif isinstance(b, dict):
                    for v in b.values():
                        if isinstance(v, list): chk(v)
                        elif isinstance(v, dict): chk(v.get('sequence', []))
    chk(d.get('sequence', []))
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/found2.json', 'w', 'utf-8') as fw:
        json.dump(found, fw, indent=2, ensure_ascii=False)
except Exception as e:
    with open('c:/Users/Administrator/Desktop/Hoc_python/scratch/found2.json', 'w') as fw:
        fw.write(f'Error: {e}')
