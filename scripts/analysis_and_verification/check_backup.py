import json

try:
    with open(r'c:\Users\Administrator\Desktop\Hoc_python\ai_fix_backup', 'r', encoding='utf-8') as f:
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
    
    with open(r'c:\Users\Administrator\Desktop\Hoc_python\debug_b2c_backup.txt', 'w', encoding='utf-8') as out:
        if b2c:
            out.write('Limit: ' + str(b2c.get('properties', {}).get('limit')) + '\n')
            out.write('Temp: ' + str(b2c.get('properties', {}).get('temperature')) + '\n')
            instr = b2c.get('properties', {}).get('instruction', '')
            out.write('Instr length: ' + str(len(instr)) + '\n')
            out.write('--- END OF INSTRUCTION ---\n')
            
            with open(r'c:\Users\Administrator\Desktop\Hoc_python\instr_backup.md', 'w', encoding='utf-8') as f2:
                f2.write(instr)
        else:
            out.write('Not found\n')
except Exception as e:
    with open(r'c:\Users\Administrator\Desktop\Hoc_python\debug_b2c_backup.txt', 'w', encoding='utf-8') as out:
        out.write('Error: ' + str(e) + '\n')
