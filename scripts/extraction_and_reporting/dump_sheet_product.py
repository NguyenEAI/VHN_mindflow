import json

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

fixing = load_json(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_fixing.json')

def find_sheet_product_block(seq):
    for node in seq:
        if node.get('name') == 'Sheet Product' and node.get('type') == 'block':
            return node
        if 'sequence' in node:
            r = find_sheet_product_block(node['sequence'])
            if r: return r
        if 'branches' in node:
            for b in node['branches'].values():
                r = find_sheet_product_block(b)
                if r: return r
    return None

sheet_product = find_sheet_product_block(fixing.get('sequence', []))

out = []
def print_node(node, indent=0):
    ind = ' ' * indent
    out.append(f"{ind}Node: {node.get('name')} (Type: {node.get('type')})")
    props = node.get('properties', {})
    
    if node.get('type') == 'qna':
        out.append(f"{ind}  Instruction: {props.get('instruction', '')[:200]}...")
        out.append(f"{ind}  varReply: {props.get('varReply')}")
    elif node.get('type') == 'python':
        out.append(f"{ind}  Expression:\n{props.get('expression', '')}")
        out.append(f"{ind}  varName: {props.get('varName')}")
    elif node.get('type') == 'botAPICall':
        out.append(f"{ind}  API Body: {props.get('api_body')}")
        out.append(f"{ind}  API Response Var: {props.get('api_response_var_name')}")
    elif node.get('type') == 'if':
        out.append(f"{ind}  Condition: {props.get('condition')}")
    elif node.get('type') == 'setVar':
        out.append(f"{ind}  varName: {props.get('varName')}")
        out.append(f"{ind}  varValue: {props.get('varValue')}")
        
    if 'sequence' in node:
        for child in node['sequence']:
            print_node(child, indent + 2)
    if 'branches' in node:
        for branch_name, branch_seq in node['branches'].items():
            out.append(f"{ind}  Branch [{branch_name}]:")
            for child in branch_seq:
                print_node(child, indent + 4)

print_node(sheet_product)

with open(r'C:\Users\Administrator\Desktop\Hoc_python\dump_sheet_product2.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
