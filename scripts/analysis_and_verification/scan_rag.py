import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
data = json.load(open('VHN_fixing.json', encoding='utf-8'))

print('=== NODES WITH RAG/KNOWLEDGE ENABLED ===')
print()

def scan(seq, path=''):
    if not isinstance(seq, list): return
    for node in seq:
        if not isinstance(node, dict): continue
        name = node.get('name', '?')
        props = node.get('properties', {})
        if node.get('type') == 'qna':
            k_aware = props.get('knowledge_aware', False)
            ch_aware = props.get('chat_history_aware', False)
            kw_search = props.get('is_include_keyword_search', False)
            dataset = props.get('dataset_uuid', '')
            limit = props.get('limit', '?')
            model = props.get('llm_alt_model', 'default')
            instr_len = len(props.get('instruction', ''))
            
            rag_flag = 'RAG=ON' if k_aware else 'RAG=OFF'
            hist_flag = f'History=ON(limit={limit})' if ch_aware else 'History=OFF'
            kw_flag = 'KW=ON' if kw_search else 'KW=OFF'
            
            print(f'  {name}:')
            print(f'    model={model} | instr={instr_len}ch | {rag_flag} | {hist_flag} | {kw_flag}')
            if dataset:
                print(f'    dataset={dataset[:20]}...')
            print()
        
        scan(node.get('sequence', []))
        if 'branches' in node:
            for b, s in node['branches'].items():
                scan(s, f'{path}/{b}')

scan(data['sequence'])
