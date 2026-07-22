import json
import traceback
import codecs

try:
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
        d = json.load(f)

    log = []
    def patch_node(nodes):
        patched = False
        if not isinstance(nodes, list): return patched
        for n in nodes:
            if not isinstance(n, dict): continue
            
            # Check name
            name = n.get('name', '')
            if name and ('AI Chuyên trách' in name or 'AI Chuyen trach' in name):
                instruction = n.get('properties', {}).get('instruction', '')
                if instruction:
                    rule = "TUYỆT ĐỐI KHÔNG tự ý thêm hoặc bổ sung bất kỳ bước skincare nào (như tẩy tế bào chết, serum đặc trị, mặt nạ...) nếu Customer KHÔNG kể. CHỈ tập trung chọn sản phẩm có công dụng giải quyết tình trạng da của khách nhưng phải ĐÚNG loại sản phẩm họ đang dùng."
                    if rule not in instruction:
                        n['properties']['instruction'] = instruction + "\n\n# QUY TẮC CẤM TỰ Ý THÊM SẢN PHẨM NGOÀI THÓI QUEN:\n" + rule
                        patched = True
                        log.append(f"Patched node: {name}")
                    else:
                        log.append(f"Already patched node: {name}")

            if 'branches' in n and isinstance(n['branches'], list):
                for b in n['branches']:
                    if isinstance(b, dict):
                        if patch_node(b.get('sequence', [])):
                            patched = True
        return patched

    if patch_node(d.get('sequence', [])):
        with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'w', 'utf-8') as fw:
            json.dump(d, fw, ensure_ascii=False, indent=2)
        log.append("SUCCESS")
    else:
        log.append("ALREADY PATCHED OR NOT FOUND")
        
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/result2.txt', 'w', 'utf-8') as f:
        f.write('\n'.join(log))

except Exception as e:
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/result2.txt', 'w', 'utf-8') as f:
        f.write(traceback.format_exc())
