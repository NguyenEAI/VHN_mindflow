"""
Deep comparison: How setVar query_data works in VHN_fixing vs VHN_DauTien_Fixed
Also dump the full sequence path from GPT-4 Query Data -> setVar -> API CALL
"""
import json

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_all_nodes(seq, path="root"):
    """Flatten all nodes with their path"""
    results = []
    for i, node in enumerate(seq):
        node_path = f"{path}[{i}]"
        results.append((node_path, node))
        if 'sequence' in node:
            results.extend(find_all_nodes(node['sequence'], f"{node_path}.seq"))
        if 'branches' in node:
            for bname, bseq in node['branches'].items():
                results.extend(find_all_nodes(bseq, f"{node_path}.branch[{bname}]"))
    return results

def dump_flow(data, label):
    print(f"\n{'='*80}")
    print(f"  FILE: {label}")
    print(f"{'='*80}")
    
    all_nodes = find_all_nodes(data.get('sequence', []))
    
    # Find all setVar nodes with query_data
    print(f"\n--- setVar nodes (session.extra.query_data) ---")
    for path, node in all_nodes:
        if node.get('type') == 'setVar' and 'query_data' in node.get('properties', {}).get('varName', ''):
            print(f"  Path: {path}")
            print(f"  ID: {node.get('id')}")
            print(f"  Name: {node.get('name')}")
            print(f"  varName: {node['properties']['varName']}")
            print(f"  varValue: {node['properties']['varValue']}")
            print()
    
    # Find all botAPICall nodes with query_data in api_body
    print(f"\n--- botAPICall nodes (using query_data) ---")
    for path, node in all_nodes:
        if node.get('type') == 'botAPICall':
            body = node.get('properties', {}).get('api_body', '')
            if 'query_data' in body:
                print(f"  Path: {path}")
                print(f"  ID: {node.get('id')}")
                print(f"  Name: {node.get('name')}")
                print(f"  api_body: {body}")
                print()
    
    # Find all GPT-4 Query Data / QnA nodes that output bot_json_query or ai_query_data
    print(f"\n--- QnA nodes (outputting query vars) ---")
    for path, node in all_nodes:
        if node.get('type') == 'qna':
            var_reply = node.get('properties', {}).get('varReply', '')
            if var_reply in ('bot_json_query', 'ai_query_data'):
                print(f"  Path: {path}")
                print(f"  ID: {node.get('id')}")
                print(f"  Name: {node.get('name')}")
                print(f"  varReply: {var_reply}")
                print(f"  json_mode: {node['properties'].get('json_mode')}")
                print()

    # Find python nodes that do json_check
    print(f"\n--- Python nodes (json_check) ---")
    for path, node in all_nodes:
        if node.get('type') == 'python':
            expr = node.get('properties', {}).get('expression', '')
            if 'json_check' in node.get('properties', {}).get('varName', '') or 'json' in expr.lower():
                print(f"  Path: {path}")
                print(f"  ID: {node.get('id')}")
                print(f"  Name: {node.get('name')}")
                print(f"  varName: {node['properties'].get('varName')}")
                print(f"  expression: {expr[:300]}")
                print()

# Load both files
fixing = load_json(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_fixing.json')
fixed = load_json(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json')

dump_flow(fixing, "VHN_fixing.json (REFERENCE - WORKING)")
dump_flow(fixed, "VHN_DauTien_Fixed.json (TARGET - BROKEN)")
