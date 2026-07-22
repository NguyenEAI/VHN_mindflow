import json
import codecs

try:
    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', 'utf-8') as f:
        d = json.load(f)

    with codecs.open('c:/Users/Administrator/Desktop/Hoc_python/scratch/all_decoded.json', 'w', 'utf-8') as fw:
        json.dump(d, fw, indent=2, ensure_ascii=False)
    print("Success")
except Exception as e:
    print("Error: " + str(e))
