import json, codecs
try:
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
        d = json.load(f)
        
    out = []
    
    def dump_nodes(nodes, indent=""):
        if not isinstance(nodes, list): return
        for n in nodes:
            if not isinstance(n, dict): continue
            
            name = n.get('name', 'UNKNOWN')
            typ = n.get('type', 'UNKNOWN')
            
            out.append(f"{indent}- [{typ}] {name}")
            
            if 'sequence' in n:
                dump_nodes(n['sequence'], indent + "  ")
                
            if 'branches' in n:
                branches = n['branches']
                if isinstance(branches, list):
                    for i, b in enumerate(branches):
                        if isinstance(b, dict):
                            out.append(f"{indent}  Branch {i}:")
                            dump_nodes(b.get('sequence', []), indent + "    ")
                elif isinstance(branches, dict):
                    for k, v in branches.items():
                        out.append(f"{indent}  Branch '{k}':")
                        if isinstance(v, list):
                            dump_nodes(v, indent + "    ")
                        elif isinstance(v, dict):
                            dump_nodes(v.get('sequence', []), indent + "    ")

            if 'branches' in n.get('properties', {}):
                branches = n['properties']['branches']
                if isinstance(branches, list):
                    for i, b in enumerate(branches):
                        if isinstance(b, dict):
                            out.append(f"{indent}  Prop Branch {i}:")
                            dump_nodes(b.get('sequence', []), indent + "    ")
                elif isinstance(branches, dict):
                    for k, v in branches.items():
                        out.append(f"{indent}  Prop Branch '{k}':")
                        if isinstance(v, list):
                            dump_nodes(v, indent + "    ")
                        elif isinstance(v, dict):
                            dump_nodes(v.get('sequence', []), indent + "    ")

    dump_nodes(d.get('sequence', []))
    
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/all_nodes_tree.txt', 'w', 'utf-8') as fw:
        fw.write("\n".join(out))
except Exception as e:
    with open('c:/Users/Administrator/Desktop/Hoc_python/scratch/all_nodes_tree.txt', 'w') as fw:
        fw.write(f'Error: {e}')
