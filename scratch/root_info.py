import json, codecs
try:
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
        d = json.load(f)
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/root_info.txt', 'w', 'utf-8') as fw:
        fw.write(f"Type: {type(d)}\n")
        if isinstance(d, dict):
            fw.write(f"Keys: {list(d.keys())}\n")
        elif isinstance(d, list):
            fw.write(f"Length: {len(d)}\n")
except Exception as e:
    with open('c:/Users/Administrator/Desktop/Hoc_python/scratch/root_info.txt', 'w') as fw:
        fw.write(f"Error: {e}\n")
