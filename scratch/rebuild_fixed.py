import json, codecs, copy

# Load both files
with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien.json', 'r', 'utf-8') as f:
    orig = json.load(f)

with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
    fixed = json.load(f)

# We need to find and extract the B2C instruction from Fixed (which has the improved prompt)
# and put it back into the original structure

def find_node_instruction(nodes, node_name):
    """Find a node by name and return its instruction"""
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

# Get the B2C instruction from FIXED
b2c_inst_fixed = find_node_instruction(fixed.get('sequence', []), 'AI Chuyên trách B2C')

# Now work with the ORIGINAL as our base
result = copy.deepcopy(orig)

# Apply the updated B2C instruction from Fixed to the original
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

if b2c_inst_fixed:
    updated = update_node_instruction(result.get('sequence', []), 'AI Chuyên trách B2C', b2c_inst_fixed)
    print(f"B2C instruction updated: {updated}")
else:
    print("WARNING: Could not find B2C instruction in fixed file")

# Also copy the Session Manager 'extra' from Fixed (which may have additional session variables)
for n in fixed.get('sequence', []):
    if n.get('type') == 'session':
        fixed_extra = n.get('properties', {}).get('extra', '')
        break

for n in result.get('sequence', []):
    if n.get('type') == 'session':
        n['properties']['extra'] = fixed_extra
        print("Session Manager extra updated")
        break

# Also copy the 'order' branch from Fixed (which has the improved order handling)
def get_flow_switch(nodes):
    if not isinstance(nodes, list): return None
    for n in nodes:
        if not isinstance(n, dict): continue
        if n.get('type') == 'flowSwitch':
            return n
        if 'sequence' in n:
            r = get_flow_switch(n['sequence'])
            if r: return r
    return None

fixed_switch = get_flow_switch(fixed.get('sequence', []))
result_switch = get_flow_switch(result.get('sequence', []))

if fixed_switch and result_switch:
    # Copy the order branch from fixed
    if 'order' in fixed_switch.get('branches', {}):
        result_switch['branches']['order'] = fixed_switch['branches']['order']
        print("Order branch copied from fixed")
    
    # Copy the b2c_consult branch from fixed  
    if 'b2c_consult' in fixed_switch.get('branches', {}):
        result_switch['branches']['b2c_consult'] = fixed_switch['branches']['b2c_consult']
        print("B2C consult branch copied from fixed")
    
    # Copy the b2b_consult branch from fixed
    if 'b2b_consult' in fixed_switch.get('branches', {}):
        result_switch['branches']['b2b_consult'] = fixed_switch['branches']['b2b_consult']
        print("B2B consult branch copied from fixed")

# Also copy blocks (Sheet, API Constants) from fixed if they exist
fixed_seq = fixed.get('sequence', [])
result_seq = result.get('sequence', [])

# Check if fixed has blocks that orig doesn't
fixed_block_names = set()
orig_block_names = set()

for n in fixed_seq:
    if n.get('type') == 'block':
        fixed_block_names.add(n.get('name'))
for n in result_seq:
    if n.get('type') == 'block':
        orig_block_names.add(n.get('name'))

missing_blocks = fixed_block_names - orig_block_names
if missing_blocks:
    print(f"Missing blocks in original: {missing_blocks}")
    # Insert missing blocks before the flowSwitch
    for n in fixed_seq:
        if n.get('type') == 'block' and n.get('name') in missing_blocks:
            # Find flowSwitch index in result
            for i, rn in enumerate(result_seq):
                if rn.get('type') == 'flowSwitch':
                    result_seq.insert(i, copy.deepcopy(n))
                    print(f"  Inserted block: {n.get('name')}")
                    break

# Copy setConst blocks
fixed_const_names = set()
orig_const_names = set()
for n in fixed_seq:
    if n.get('type') == 'block':
        for sn in n.get('sequence', []):
            if sn.get('type') == 'setConst':
                fixed_const_names.add(sn.get('name'))
for n in result_seq:
    if n.get('type') == 'block':
        for sn in n.get('sequence', []):
            if sn.get('type') == 'setConst':
                orig_const_names.add(sn.get('name'))

# Save result
with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'w', 'utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\nDone! Saved to VHN_DauTien_Fixed.json")
