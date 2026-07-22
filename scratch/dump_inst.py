import json, codecs
try:
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
        d = json.load(f)

    def extract_b2c_inst(nodes):
        if not isinstance(nodes, list): return
        for n in nodes:
            if not isinstance(n, dict): continue
            
            name = n.get('name', 'UNKNOWN')
            if 'B2C' in name and 'Chuyên' in name:
                inst = n.get('properties', {}).get('instruction', '')
                with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/b2c_inst_full.txt', 'w', 'utf-8') as fw:
                    fw.write(inst)
                return True
                
            if 'sequence' in n:
                if extract_b2c_inst(n['sequence']): return True
                
            if 'branches' in n.get('properties', {}):
                branches = n.get('properties', {}).get('branches')
                if isinstance(branches, list):
                    for b in branches:
                        if isinstance(b, dict):
                            if extract_b2c_inst(b.get('sequence', [])): return True
                elif isinstance(branches, dict):
                    if extract_b2c_inst(branches.get('true', [])): return True
                    if extract_b2c_inst(branches.get('false', [])): return True
                    
            if n.get('type') == 'flowSwitch':
                # The branches in flowSwitch are keys in the node itself!
                for k, v in n.items():
                    if isinstance(v, list):
                        if extract_b2c_inst(v): return True
        return False
        
    res = extract_b2c_inst(d.get('sequence', []))
    if not res:
        with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/b2c_inst_full.txt', 'w', 'utf-8') as fw:
            fw.write('Not found!')
except Exception as e:
    with open('c:/Users/Administrator/Desktop/Hoc_python/scratch/b2c_inst_full.txt', 'w') as fw:
        fw.write(f'Error: {e}')
