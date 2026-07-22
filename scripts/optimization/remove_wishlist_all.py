import json

with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def clean_product_wishlist(obj):
    if isinstance(obj, dict):
        # Allow GPT-4o Mini to keep product_wishlist because it is the recommend_product LLM
        # Wait, the node is named "GPT-4o Mini". Let's check its name.
        if obj.get('name') != 'GPT-4o Mini':
            for k, v in obj.items():
                if k == 'instruction' and isinstance(v, str):
                    text_to_remove = "## Product List\n\"\"\"\n{{session.extra.product_wishlist}}\n\"\"\"\n"
                    if text_to_remove in v:
                        obj[k] = v.replace(text_to_remove, "")
                        print(f"Removed product_wishlist from node: {obj.get('name', 'Unknown')}")
                    
                    text_to_remove2 = "## Product List\n\"\"\"\n{{session.extra.product_wishlist}}\n\"\"\"\n\n"
                    if text_to_remove2 in v:
                        obj[k] = v.replace(text_to_remove2, "")
                        print(f"Removed product_wishlist from node: {obj.get('name', 'Unknown')} (variation)")
                
                clean_product_wishlist(v)
        else:
            print("Skipping node 'GPT-4o Mini' as it needs product_wishlist")
            
    elif isinstance(obj, list):
        for v in obj:
            clean_product_wishlist(v)

clean_product_wishlist(data)

with open('VHN_fixing.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
