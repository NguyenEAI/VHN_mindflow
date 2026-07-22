import json, codecs

# Load the file
with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
    data = json.load(f)

# Find the Session Manager node
for n in data.get('sequence', []):
    if n.get('type') == 'session':
        # Parse the 'extra' JSON string
        extra_str = n.get('properties', {}).get('extra', '{}')
        try:
            extra_dict = json.loads(extra_str)
            if 'product_information' not in extra_dict:
                extra_dict['product_information'] = ''
                # Re-serialize and update
                n['properties']['extra'] = json.dumps(extra_dict, ensure_ascii=False)
                print("Successfully added 'product_information' to session.extra")
            else:
                print("'product_information' already exists in session.extra")
        except json.JSONDecodeError as e:
            print(f"Failed to parse session extra JSON: {e}")
        break

# Save it back
with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'w', 'utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
