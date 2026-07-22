import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def generate_hbs(node, out):
    if node['type'] == 'if':
        out.append(f'{{{{#if {node.get("properties", {}).get("condition", "true")} }}}}')
        if 'branches' in node and 'true' in node['branches']:
            for child in node['branches']['true']:
                generate_hbs(child, out)
        out.append(f'{{{{else}}}}')
        if 'branches' in node and 'false' in node['branches']:
            for child in node['branches']['false']:
                generate_hbs(child, out)
        out.append(f'{{{{/if}}}}')
    elif node['type'] == 'block':
        out.append(f'{{{{#block name="{node.get("name")}" }}}}')
        if 'sequence' in node:
            for child in node['sequence']:
                generate_hbs(child, out)
        out.append(f'{{{{/block}}}}')
    elif node['type'] in ['qna', 'python', 'setVar', 'botAPICall', 'recall']:
        pass
    else:
        if 'sequence' in node:
            for child in node['sequence']:
                generate_hbs(child, out)
        if 'branches' in node:
            for b in node['branches'].values():
                for child in b:
                    generate_hbs(child, out)

out = []
for node in data.get('sequence', []):
    generate_hbs(node, out)

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\simulate_hbs.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
    
# Count if/block
if_count = 0
block_count = 0
for line in out:
    if '{{#if' in line: if_count += 1
    if '{{/if}}' in line: if_count -= 1
    if '{{#block' in line: block_count += 1
    if '{{/block}}' in line: block_count -= 1

print(f"if balance: {if_count}")
print(f"block balance: {block_count}")
