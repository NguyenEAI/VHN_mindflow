import json
import codecs

try:
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/all_decoded.json', 'r', 'utf-8') as f:
        lines = f.readlines()
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/b2c_search_out2.txt', 'w', 'utf-8') as fw:
        for i, line in enumerate(lines):
            if 'AI Chuyên trách' in line or 'AI Chuyen trach' in line:
                fw.write(f'Found at line {i+1}: {line.strip()}\n')
    print("Done")
except Exception as e:
    print("Error: " + str(e))
