import json
import codecs

try:
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
        d = json.load(f)

    blocks = []
    def get_blocks(nodes):
        if not isinstance(nodes, list): return
        for n in nodes:
            if not isinstance(n, dict): continue
            if n.get('type') == 'block':
                blocks.append(n)
            if 'branches' in n and isinstance(n['branches'], list):
                for b in n['branches']:
                    if isinstance(b, dict):
                        get_blocks(b.get('sequence', []))

    get_blocks(d.get('sequence', []))
    
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/all_blocks.json', 'w', 'utf-8') as fw:
        json.dump(blocks, fw, indent=2, ensure_ascii=False)
    print("Success, found " + str(len(blocks)) + " blocks")
except Exception as e:
    print("Error: " + str(e))
