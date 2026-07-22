import json
import codecs

try:
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
        d = json.load(f)

    types = set()
    def get_types(nodes):
        if not isinstance(nodes, list): return
        for n in nodes:
            if not isinstance(n, dict): continue
            if 'type' in n: types.add(n['type'])
            if 'branches' in n and isinstance(n['branches'], list):
                for b in n['branches']:
                    if isinstance(b, dict):
                        get_types(b.get('sequence', []))

    get_types(d.get('sequence', []))
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/node_types2.txt', 'w', 'utf-8') as fw:
        fw.write('\n'.join(list(types)))
    print("Success")
except Exception as e:
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/node_types2.txt', 'w', 'utf-8') as fw:
        fw.write("Error: " + str(e))
    print("Error")
