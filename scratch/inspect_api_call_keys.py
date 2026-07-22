import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
if_json_check_node = data['sequence'][5]['branches']['b2c_consult'][3]['branches']['true'][0]['sequence'][2]
api_call_node = if_json_check_node['branches']['true'][2]

out.append('API Call Node keys: ' + str(api_call_node['properties'].keys()))
out.append('API Call URL/Endpoint: ' + str(api_call_node['properties'].get('endpoint') or api_call_node['properties'].get('request_url')))

with open(r'C:\Users\Administrator\Desktop\Hoc_python\scratch\inspect_api_call_keys.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
