import json

with open(r'c:\Users\Administrator\Desktop\Hoc_python\ai.txt', 'r', encoding='utf-8') as f:
    data = json.load(f)

def find_block(obj, block_id):
    if isinstance(obj, dict):
        if obj.get('id') == block_id: return obj
        for k, v in obj.items():
            res = find_block(v, block_id)
            if res: return res
    elif isinstance(obj, list):
        for item in obj:
            res = find_block(item, block_id)
            if res: return res
    return None

b2c = find_block(data, '8a045fd50c088e3adf5f000f40c21d66')
if b2c:
    instr = b2c.get('properties', {}).get('instruction', '')
    with open(r'c:\Users\Administrator\Desktop\Hoc_python\instr.md', 'w', encoding='utf-8') as f:
        f.write(instr)
