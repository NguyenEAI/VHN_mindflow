import json
import io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

filepath = 'VHN_fixing.json'
with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Loaded JSON.")

def find_const_node(seq, const_name):
    if not isinstance(seq, list): return None
    for node in seq:
        if not isinstance(node, dict): continue
        if node.get('properties', {}).get('constName') == const_name:
            return node
        found = find_const_node(node.get('sequence', []), const_name)
        if found: return found
        for k, v in node.get('properties', {}).items():
            if isinstance(v, list):
                found = find_const_node(v, const_name)
                if found: return found
        if 'branches' in node:
            for k, v in node['branches'].items():
                found = find_const_node(v, const_name)
                if found: return found
    return None

node_pl = find_const_node(data['sequence'], 'product_list')
if node_pl:
    print(f"Found product_list with value len: {len(node_pl['properties']['constValue'])}")
    node_pl['properties']['constValue'] = ''

node_cb = find_const_node(data['sequence'], 'company_branch')
if node_cb:
    print(f"Found company_branch with value len: {len(node_cb['properties']['constValue'])}")
    node_cb['properties']['constValue'] = ''

def find_node(seq, name):
    if not isinstance(seq, list): return None
    for node in seq:
        if not isinstance(node, dict): continue
        if node.get('name') == name: return node
        found = find_node(node.get('sequence', []), name)
        if found: return found
        for k, v in node.get('properties', {}).items():
            if isinstance(v, list):
                found = find_node(v, name)
                if found: return found
        if 'branches' in node:
            for k, v in node['branches'].items():
                found = find_node(v, name)
                if found: return found
    return None

mgr = find_node(data['sequence'], 'MANAGER')
if mgr:
    for node in mgr.get('sequence', []):
        if isinstance(node, dict) and node.get('type') == 'qna':
            instr = node['properties'].get('instruction', '')
            old_str = '- When Customer ask about any of {{ product_list }}, Assistant MUST ALWAYS chọn phase `recommend_product` và chọn "need_product_info" là `yes` để Sales Staff có đầy đủ thông tin trả lời User.'
            new_str = '- Khi Customer nhắc đến, hỏi về, hoặc mô tả một sản phẩm cụ thể (ví dụ: kem dưỡng, serum, kem chống nắng, trị mụn, trị nám, tên thương hiệu, bộ sản phẩm peel da...), Assistant MUST ALWAYS chọn phase `recommend_product` và đặt "need_product_info" là "yes" để gọi API lấy dữ liệu.'
            if old_str in instr:
                instr = instr.replace(old_str, new_str)
                node['properties']['instruction'] = instr
                print('Updated MANAGER instruction successfully.')
            else:
                print('Could not find exact string in MANAGER instruction to replace. Looking for product_list...')
                if '{{ product_list }}' in instr:
                    print('Found {{ product_list }} but not the exact sentence.')
            
            if node['properties'].get('llm_alt_model') == 'gpt-4':
                node['properties']['llm_alt_model'] = 'gpt-4o-mini'
                print('Updated MANAGER model to gpt-4o-mini')

parallel_node = find_node(data['sequence'], 'Parallel')
if parallel_node and 'branches' in parallel_node:
    for b_name, b_seq in parallel_node['branches'].items():
        for node in b_seq:
            if isinstance(node, dict) and node.get('type') == 'qna':
                instr = node['properties'].get('instruction', '')
                if '{{company_branch}}' in instr:
                    instr = instr.replace('{{company_branch}}', '')
                    node['properties']['instruction'] = instr
                    print(f'Removed company_branch from {b_name} instruction.')
                
                if b_name == 'gather_requirement':
                    if node['properties'].get('llm_alt_model') == 'gpt-4':
                        node['properties']['llm_alt_model'] = 'gpt-4o'
                        print('Updated Gather Requirement to gpt-4o')
                if b_name == 'recommend_product':
                    if node['properties'].get('llm_alt_model') == 'gpt-4':
                        node['properties']['llm_alt_model'] = 'gpt-4o'
                        print('Updated Recommend Product to gpt-4o')
                    if node['properties'].get('max_tokens') == '5000':
                        node['properties']['max_tokens'] = '2000'
                        print('Reduced Recommend Product max_tokens to 2000')

conds = parallel_node['properties'].get('conditions', {})
if 'handover' in conds:
    old_handover = conds['handover']
    if 'OR' in old_handover or 'or' in old_handover:
        conds['handover'] = 'session.extra.previous_manager_decision.phase == "handover"'
        print('Fixed handover OR logic.')
if 'agency_gather_info' in conds:
    old_agency = conds['agency_gather_info']
    if 'OR' in old_agency or 'or' in old_agency:
        conds['agency_gather_info'] = 'session.extra.previous_manager_decision.phase == "agency_gather_info"'
        print('Fixed agency_gather_info OR logic.')

query_node = find_node(data['sequence'], 'GPT-4 Query Data')
if query_node and query_node['properties'].get('llm_alt_model') == 'gpt-4':
    query_node['properties']['llm_alt_model'] = 'gpt-4o-mini'
    print('Updated Query Data model to gpt-4o-mini')

analysis_node = find_node(data['sequence'], 'GPT-4 Analysis')
if analysis_node and analysis_node['properties'].get('llm_alt_model') == 'gpt-4':
    analysis_node['properties']['llm_alt_model'] = 'gpt-4o-mini'
    print('Updated Analysis model to gpt-4o-mini')

with open('VHN_fixing.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
print('Saved updated VHN_fixing.json')
