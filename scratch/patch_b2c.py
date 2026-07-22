import json
import codecs

try:
    file_path = 'c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json'
    with codecs.open(file_path, 'r', 'utf-8') as f:
        d = json.load(f)

    def patch_node(nodes):
        if not isinstance(nodes, list): return False
        for n in nodes:
            if not isinstance(n, dict): continue
            if n.get('name') == 'AI Chuyên trách B2C':
                instruction = n.get('properties', {}).get('instruction', '')
                
                # We will add a strict rule after "## Nguyên tắc 1-1 MAPPING với thói quen skincare khách kể:"
                # Or at the end of "## Nguyên tắc 1-1 MAPPING"
                
                rule_text = "\nTUYỆT ĐỐI KHÔNG tự ý thêm/bổ sung bất kỳ bước nào (ví dụ: tẩy tế bào chết, serum, mask...) nếu Customer KHÔNG kể. CHỈ tập trung chọn sản phẩm có công dụng giải quyết tình trạng da của khách nhưng phải ĐÚNG loại sản phẩm họ đang dùng.\n"
                
                # Check if it's already patched
                if rule_text.strip() not in instruction:
                    new_instruction = instruction.replace(
                        "KHÔNG ĐƯỢC BỎ SÓT bước nào.",
                        "KHÔNG ĐƯỢC BỎ SÓT bước nào. " + rule_text
                    )
                    n['properties']['instruction'] = new_instruction
                    return True
            
            if 'branches' in n and isinstance(n['branches'], list):
                for b in n['branches']:
                    if isinstance(b, dict):
                        if patch_node(b.get('sequence', [])):
                            return True
        return False

    if patch_node(d.get('sequence', [])):
        with codecs.open(file_path, 'w', 'utf-8') as fw:
            json.dump(d, fw, ensure_ascii=False, indent=2)
        print("Patched successfully!")
    else:
        print("Could not find or already patched")

except Exception as e:
    print("Error:", e)
