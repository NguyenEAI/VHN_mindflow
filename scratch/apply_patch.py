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
                
                # Rule to append
                rule_text = "\n\n## QUY TẮC CẤM TỰ Ý THÊM BƯỚC:\nTUYỆT ĐỐI KHÔNG tự ý đề xuất thêm/bổ sung bất kỳ bước skincare nào (ví dụ: tẩy tế bào chết, serum, toner...) nếu Customer KHÔNG chủ động nhắc đến bước đó trong thói quen của họ. CHỈ tập trung chọn sản phẩm có công dụng giải quyết tình trạng da của khách nhưng phải thuộc ĐÚNG các bước họ đang dùng."
                
                if rule_text not in instruction:
                    # Append it right before "# QUY TẮC BẮT BUỘC VỀ SỐ LƯỢNG & LOẠI SẢN PHẨM ĐỀ XUẤT (CỰC KỲ QUAN TRỌNG)"
                    target = "# QUY TẮC BẮT BUỘC VỀ SỐ LƯỢNG & LOẠI SẢN PHẨM ĐỀ XUẤT (CỰC KỲ QUAN TRỌNG)"
                    
                    if target in instruction:
                        instruction = instruction.replace(target, rule_text + "\n\n" + target)
                        n['properties']['instruction'] = instruction
                        return True
                    else:
                        print("Target string not found in instruction")
                        return False
                else:
                    print("Already patched")
                    return False
            
            if 'branches' in n and isinstance(n['branches'], list):
                for b in n['branches']:
                    if isinstance(b, dict):
                        if patch_node(b.get('sequence', [])):
                            return True
        return False

    if patch_node(d.get('sequence', [])):
        with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'w', 'utf-8') as fw:
            json.dump(d, fw, ensure_ascii=False, indent=2)
        print("Patched successfully!")

except Exception as e:
    print("Error:", e)
