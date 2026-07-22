import json
with open('c:/Users/Administrator/Desktop/Hoc_python/VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
def print_tree(data, level=0):
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, list):
                print('  '*level + k + ' (list of ' + str(len(v)) + ')')
                if len(v) > 0: print_tree(v[0], level+1)
            elif isinstance(v, dict):
                print('  '*level + k + ' (dict)')
                print_tree(v, level+1)
            else:
                pass
print('Root keys:', list(d.keys()))
print_tree(d)
