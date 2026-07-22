import json
import traceback

try:
    with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_fixing.json', 'r', encoding='utf-8') as f:
        fixing = json.load(f)
    print("Keys:", list(fixing.keys()))
    if 'sequence' in fixing:
        print("Sequence length:", len(fixing['sequence']))
    if 'nodes' in fixing:
        print("Nodes length:", len(fixing['nodes']))
except Exception as e:
    traceback.print_exc()
