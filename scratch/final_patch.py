import json
import traceback

def run():
    try:
        with open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
            d = json.load(f)
            
        def patch_node(nodes):
            if not isinstance(nodes, list): return False
            for n in nodes:
                if not isinstance(n, dict): continue
                if n.get('name') == 'AI Chuyên trách B2C':
                    instruction = n.get('properties', {}).get('instruction', '')
                    rule = 'TUYỆT ĐỐI KHÔNG tự ý thêm/bổ sung bất kỳ bước nào (ví dụ: tẩy tế bào chết, serum, toner...) nếu Customer KHÔNG chủ động nhắc đến trong thói quen skincare của họ. CHỈ tập trung chọn sản phẩm có công dụng giải quyết tình trạng da của khách nhưng ĐẢM BẢO sản phẩm đó phải thuộc ĐÚNG các bước họ đang dùng.'
                    if rule not in instruction:
                        n['properties']['instruction'] = instruction + '\n\n# QUY TẮC BỔ SUNG QUAN TRỌNG:\n' + rule
                        return True
                    return False
                if 'branches' in n and isinstance(n['branches'], list):
                    for b in n['branches']:
                        if isinstance(b, dict):
                            if patch_node(b.get('sequence', [])):
                                return True
            return False

        if patch_node(d.get('sequence', [])):
            with open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'w', encoding='utf-8') as fw:
                json.dump(d, fw, ensure_ascii=False, indent=2)
            return "SUCCESS"
        else:
            return "NOT_FOUND_OR_ALREADY_PATCHED"
    except Exception as e:
        return "ERROR: " + traceback.format_exc()

res = run()
with open('c:/Users/Administrator/Desktop/Hoc_python/scratch/final_result.txt', 'w', encoding='utf-8') as f:
    f.write(res)
