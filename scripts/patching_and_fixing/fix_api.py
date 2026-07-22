import json

with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

updated = False
def fix_api_body(obj):
    global updated
    if isinstance(obj, dict):
        if obj.get('name') == 'API CALL PRODUCT DATA' and obj.get('type') == 'botAPICall':
            body = obj.get('properties', {}).get('api_body', '')
            if '"vendor": "none"' in body:
                # Replace with the actual variable
                new_body = body.replace('"vendor": "none"', '"vendor": "{{ session.extra.query_data.vendor }}"')
                obj['properties']['api_body'] = new_body
                updated = True
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                fix_api_body(v)
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, (dict, list)):
                fix_api_body(v)

fix_api_body(data)

if updated:
    with open('VHN_fixing.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("Successfully fixed hardcoded vendor in API CALL PRODUCT DATA nodes.")
else:
    print("Could not find hardcoded vendor in API CALL PRODUCT DATA nodes.")
