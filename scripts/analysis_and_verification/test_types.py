import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

fixing = json.load(open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_fixing.json', encoding='utf-8'))
types = set()
def get_types(seq):
    for n in seq:
        types.add(n.get('type'))
        if 'sequence' in n: get_types(n['sequence'])
        if 'branches' in n:
            for b in n['branches'].values(): get_types(b)
get_types(fixing.get('sequence', []))
print("Node types:", types)
