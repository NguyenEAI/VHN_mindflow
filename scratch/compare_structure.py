import json, codecs

def get_structure(nodes, path=""):
    result = []
    if not isinstance(nodes, list): return result
    for i, n in enumerate(nodes):
        if not isinstance(n, dict): continue
        name = n.get('name', 'UNKNOWN')
        typ = n.get('type', 'UNKNOWN')
        ctype = n.get('componentType', 'UNKNOWN')
        nid = n.get('id', 'UNKNOWN')
        
        props_keys = sorted(n.get('properties', {}).keys())
        
        entry = f"{path}[{i}] {typ}/{ctype} '{name}' id={nid} props={props_keys}"
        result.append(entry)
        
        if 'sequence' in n:
            result.extend(get_structure(n['sequence'], f"{path}[{i}].seq"))
            
        if 'branches' in n:
            branches = n['branches']
            if isinstance(branches, dict):
                for k in sorted(branches.keys()):
                    v = branches[k]
                    if isinstance(v, list):
                        result.extend(get_structure(v, f"{path}[{i}].br.{k}"))

    return result

for fname in ['VHN_DauTien.json', 'VHN_DauTien_Fixed.json']:
    with codecs.open(f'c:/Users/Administrator/Desktop/Hoc_python/{fname}', 'r', 'utf-8') as f:
        d = json.load(f)
    
    structure = get_structure(d.get('sequence', []))
    outname = fname.replace('.json', '_structure.txt')
    with codecs.open(f'c:/Users/Administrator/Desktop/Hoc_python/scratch/{outname}', 'w', 'utf-8') as fw:
        fw.write('\n'.join(structure))
    print(f"{fname}: {len(structure)} nodes")
