import json, codecs, copy

# Load original file
with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien.json', 'r', 'utf-8') as f:
    orig = json.load(f)

# Load the fixed file (the one that had the good instruction but broken structure)
with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
    fixed = json.load(f)

def find_node_instruction(nodes, node_name):
    if not isinstance(nodes, list): return None
    for n in nodes:
        if not isinstance(n, dict): continue
        if n.get('name') == node_name:
            return n.get('properties', {}).get('instruction', '')
        if 'sequence' in n:
            r = find_node_instruction(n['sequence'], node_name)
            if r is not None: return r
        if 'branches' in n:
            b = n['branches']
            if isinstance(b, dict):
                for v in b.values():
                    if isinstance(v, list):
                        r = find_node_instruction(v, node_name)
                        if r is not None: return r
    return None

def update_node_instruction(nodes, node_name, new_instruction):
    if not isinstance(nodes, list): return False
    for n in nodes:
        if not isinstance(n, dict): continue
        if n.get('name') == node_name:
            n['properties']['instruction'] = new_instruction
            return True
        if 'sequence' in n:
            if update_node_instruction(n['sequence'], node_name, new_instruction): return True
        if 'branches' in n:
            b = n['branches']
            if isinstance(b, dict):
                for v in b.values():
                    if isinstance(v, list):
                        if update_node_instruction(v, node_name, new_instruction): return True
    return False

# 1. Get the improved B2C instruction
b2c_inst = find_node_instruction(fixed.get('sequence', []), 'AI Chuyên trách B2C')

# 2. Start fresh with original structure
result = copy.deepcopy(orig)

# 3. Apply ONLY the improved B2C instruction
if b2c_inst:
    success = update_node_instruction(result.get('sequence', []), 'AI Chuyên trách B2C', b2c_inst)
    print(f"Updated B2C instruction: {success}")
else:
    print("WARNING: Could not find B2C instruction")

# Save as Fixed
with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'w', 'utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("Saved clean VHN_DauTien_Fixed.json with original flat structure + updated B2C instructions.")
