import json

with open('VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def fix_wishlist(seq):
    changed = False
    for node in seq:
        if node.get('name') == 'Format Wishlist' and node.get('type') == 'python':
            expr = node['properties'].get('expression', '')
            if 'PRODUCTS[:10]' in expr:
                node['properties']['expression'] = expr.replace('if len(PRODUCTS) > 10: PRODUCTS = PRODUCTS[:10]', '# no limit')
                changed = True
                print(f"Fixed {node['id']}")
            elif 'PRODUCTS[:20]' in expr:
                node['properties']['expression'] = expr.replace('if len(PRODUCTS) > 20: PRODUCTS = PRODUCTS[:20]', '# no limit')
                changed = True
                print(f"Fixed {node['id']}")
        
        if 'sequence' in node:
            if fix_wishlist(node['sequence']): changed = True
        if 'branches' in node:
            for b in node['branches'].values():
                if fix_wishlist(b): changed = True
    return changed

if fix_wishlist(data.get('sequence', [])):
    with open('VHN_DauTien_Fixed.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("PATCHED WISHLIST")
else:
    print("NO CHANGES NEEDED")
