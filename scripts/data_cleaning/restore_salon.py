def restore_field(filename, val, is_b2c):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    out = []
    # Add back header for b2c_cleaned if it's missing
    if is_b2c and not lines[0].startswith('# DANH SÁCH'):
        out.append('# DANH SÁCH SẢN PHẨM B2C (is_salon_product = False)\n')
        out.append('\n')
        out.append('**Tổng số sản phẩm B2C:** 234\n')
        out.append('---\n')
        
    for i, line in enumerate(lines):
        # Prevent duplicate insertion if run multiple times
        if '- **is_salon_product:**' in line:
            continue
            
        out.append(line)
        
        # Insert after the last metadata field (- **)
        if line.startswith('- **'):
            next_is_meta = False
            if i + 1 < len(lines) and lines[i+1].startswith('- **'):
                next_is_meta = True
                
            if not next_is_meta:
                out.append(f'- **is_salon_product:** {val}\n')
                
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("".join(out))

restore_field(r'c:\Users\Administrator\Desktop\Hoc_python\data\b2b.txt', 'True', False)
restore_field(r'c:\Users\Administrator\Desktop\Hoc_python\data\b2c_cleaned.txt', 'False', True)

print("Da phuc hoi thanh cong!")
