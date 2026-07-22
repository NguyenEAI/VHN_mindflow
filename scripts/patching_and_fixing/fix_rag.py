import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
data = json.load(open('VHN_fixing.json', encoding='utf-8'))

# Nodes that SHOULD KEEP RAG on
KEEP_RAG = ['GPT-4o Mini QnA', 'GPT-4 Recommend Product']

changes = []

def fix_rag(seq):
    if not isinstance(seq, list): return
    for node in seq:
        if not isinstance(node, dict): continue
        name = node.get('name', '?')
        props = node.get('properties', {})
        
        if node.get('type') == 'qna':
            k_aware = props.get('knowledge_aware', False)
            kw_search = props.get('is_include_keyword_search', False)
            
            if k_aware and name not in KEEP_RAG:
                props['knowledge_aware'] = False
                props['knowledge'] = ''
                if kw_search:
                    props['is_include_keyword_search'] = False
                changes.append(f'RAG OFF: {name}')
            elif k_aware and name in KEEP_RAG:
                changes.append(f'RAG KEPT: {name}')
        
        fix_rag(node.get('sequence', []))
        if 'branches' in node:
            for b, s in node['branches'].items():
                fix_rag(s)

fix_rag(data['sequence'])

print('=== CHANGES MADE ===')
for c in changes:
    print(f'  {c}')

# Save
with open('VHN_fixing.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
print(f'\nSaved VHN_fixing.json ({len(changes)} changes)')

# Verify
print('\n=== VERIFICATION ===')
data2 = json.load(open('VHN_fixing.json', encoding='utf-8'))
def verify(seq):
    if not isinstance(seq, list): return
    for node in seq:
        if not isinstance(node, dict): continue
        if node.get('type') == 'qna':
            name = node.get('name', '?')
            rag = node['properties'].get('knowledge_aware', False)
            kw = node['properties'].get('is_include_keyword_search', False)
            status = 'RAG=ON' if rag else 'RAG=OFF'
            kw_s = 'KW=ON' if kw else 'KW=OFF'
            print(f'  {name}: {status} | {kw_s}')
        verify(node.get('sequence', []))
        if 'branches' in node:
            for b, s in node['branches'].items():
                verify(s)
verify(data2['sequence'])
