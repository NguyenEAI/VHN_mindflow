import json

def print_urls():
    with open(r'c:\Users\Administrator\Desktop\Hoc_python\VHN_backup.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    sheet_block = next((n for n in data['sequence'] if n.get('name') == 'Sheet'), None)
    if sheet_block:
        for node in sheet_block.get('sequence', []):
            print(f"Sheet block const: {node.get('properties', {}).get('constName')} = {node.get('properties', {}).get('constValue')}")
            
    # Print the api_body of the botAPICall inside "Lấy thông tin sản phẩm" -> "Sheet Product" -> "Search sản phẩm?" -> API call
    prod_block = next((n for n in data['sequence'] if n.get('name') == 'Lấy thông tin sản phẩm'), None)
    if prod_block:
        try:
            search_s = prod_block['sequence'][0]['branches']['true'][0]['sequence'][2]
            true_branch = search_s['branches']['true']
            for n in true_branch:
                if n.get('type') == 'botAPICall':
                    print("API Body in true branch:")
                    print(n.get('properties', {}).get('api_body'))
            false_branch = search_s['branches']['false']
            for n in false_branch:
                if n.get('type') == 'botAPICall':
                    print("API Body in false branch:")
                    print(n.get('properties', {}).get('api_body'))
        except Exception as e:
            print("Error finding api body:", e)

print_urls()
