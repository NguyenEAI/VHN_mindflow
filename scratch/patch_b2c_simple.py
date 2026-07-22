import json
import codecs

try:
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
        d = json.load(f)

    def patch_node(nodes):
        if not isinstance(nodes, list): return False
        for n in nodes:
            if not isinstance(n, dict): continue
            if n.get('name') == 'AI Chuyên trách B2C':
                instruction = n.get('properties', {}).get('instruction', '')
                
                rule_text = "TUYỆT ĐỐI KHÔNG được tự ý thêm bất kỳ bước chăm sóc da nào (như tẩy tế bào chết, serum, toner...) nếu Customer KHÔNG chủ động nhắc đến trong thói quen skincare hiện tại của họ. CHỈ đề xuất đúng các loại sản phẩm thuộc các bước mà Customer đã nêu, và đảm bảo sản phẩm đó có công dụng phù hợp để giải quyết tình trạng da của họ."
                
                if rule_text not in instruction:
                    # Just append it at the end of the instruction for safety
                    instruction += "\n\n# QUY TẮC BỔ SUNG:\n" + rule_text
                    n['properties']['instruction'] = instruction
                    return True
                else:
                    return False
            
            if 'branches' in n and isinstance(n['branches'], list):
                for b in n['branches']:
                    if isinstance(b, dict):
                        if patch_node(b.get('sequence', [])):
                            return True
        return False

    patched = patch_node(d.get('sequence', []))
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/patch_log.txt', 'w', 'utf-8') as fw:
        if patched:
            with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'w', 'utf-8') as fw_json:
                json.dump(d, fw_json, ensure_ascii=False, indent=2)
            fw.write("Patched successfully")
        else:
            fw.write("Already patched or not found")
except Exception as e:
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/patch_log.txt', 'w', 'utf-8') as fw:
        fw.write("Error: " + str(e))
