import json

with open('VHN_fixing.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for node in data.get('sequence', []):
    if node.get('type') == 'block':
        for task in node.get('sequence', []):
            if task.get('name') == 'GPT-4 MANAGER':
                inst = task['properties']['instruction']
                
                # Remove Product List section
                text_to_remove = "## Product List\n\"\"\"\n{{session.extra.product_wishlist}}\n\"\"\"\n"
                if text_to_remove in inst:
                    inst = inst.replace(text_to_remove, "")
                    print("Removed product_wishlist from GPT-4 MANAGER")
                
                task['properties']['instruction'] = inst
                
    elif node.get('type') == 'switch':
        for branch_name, tasks in node.get('branches', {}).items():
            for task in tasks:
                if task.get('name') == 'GPT-4o Mini Offtopic':
                    inst = task['properties']['instruction']
                    
                    text_to_remove = "## Product List\n\"\"\"\n{{session.extra.product_wishlist}}\n\"\"\"\n\n"
                    if text_to_remove in inst:
                        inst = inst.replace(text_to_remove, "")
                        print("Removed product_wishlist from GPT-4o Mini Offtopic")
                    
                    task['properties']['instruction'] = inst

with open('VHN_fixing.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
