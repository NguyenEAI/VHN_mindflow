import re

def insert_field(filename, value):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by product header "## "
    parts = content.split('\n## ')
    new_parts = [parts[0]] # header
    
    for part in parts[1:]:
        lines = part.split('\n')
        # Find the last line starting with "- **"
        last_meta_idx = -1
        for i, line in enumerate(lines):
            if line.startswith('- **'):
                last_meta_idx = i
        
        if last_meta_idx != -1:
            # Insert the is_salon_product field right after the last meta line
            lines.insert(last_meta_idx + 1, f'- **is_salon_product:** {value}')
            
        new_parts.append('\n'.join(lines))
        
    new_content = '\n## '.join(new_parts)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)

# Apply to B2C
insert_field(r'c:\Users\Administrator\Desktop\Hoc_python\data\b2c_cleaned.txt', 'False')

# Apply to B2B
insert_field(r'c:\Users\Administrator\Desktop\Hoc_python\data\b2b.txt', 'True')

print("Da them lai truong is_salon_product cho ca 2 file thanh cong!")
