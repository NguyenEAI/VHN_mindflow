import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

fixing = json.load(open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_fixing.json', encoding='utf-8'))
def find_api_calls(seq):
    for n in seq:
        if n.get('type') == 'botAPICall':
            print("Name:", n.get('name'))
            print("URL:", n.get('properties', {}).get('api_url'))
            print("Body:", repr(n.get('properties', {}).get('api_body', '')))
            print("Response Var:", n.get('properties', {}).get('api_response_var_name'))
            print("-" * 40)
        if 'sequence' in n: find_api_calls(n['sequence'])
        if 'branches' in n:
            for b in n['branches'].values(): find_api_calls(b)
find_api_calls(fixing.get('sequence', []))
