import json, codecs

with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
    d = json.load(f)

def check_instructions(nodes, path=''):
    if not isinstance(nodes, list): return
    for i, n in enumerate(nodes):
        if not isinstance(n, dict): continue
        name = n.get('name', '')
        inst = n.get('properties', {}).get('instruction', '')
        
        if inst:
            # Find single { that are NOT part of {{ }}
            singles = []
            j = 0
            while j < len(inst):
                if inst[j] == '{':
                    if j + 1 < len(inst) and inst[j+1] == '{':
                        # This is {{ - skip it
                        j += 2
                        continue
                    else:
                        # Single { 
                        context = inst[max(0,j-30):min(len(inst),j+30)]
                        singles.append((j, context))
                j += 1
                        
            if singles:
                print(f'NODE: {name}')
                for pos, ctx in singles[:5]:
                    print(f'  Single brace at pos {pos}: ...{repr(ctx)}...')
                print()
        
        if 'sequence' in n: check_instructions(n['sequence'], f'{path}[{i}].seq')
        if 'branches' in n:
            b = n['branches']
            if isinstance(b, dict):
                for k, v in b.items():
                    if isinstance(v, list): check_instructions(v, f'{path}[{i}].br.{k}')

import sys
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
check_instructions(d.get('sequence', []))
