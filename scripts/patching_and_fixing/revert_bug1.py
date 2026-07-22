"""
Revert BUG #1: Move flowSwitch + filters BACK to top-level sequence.
flowSwitch MUST be at top-level, NOT nested inside if.
Keep all other fixes intact.
"""
import json

INPUT_FILE = r'c:\Users\Administrator\Desktop\Hoc_python\VHN_Optimized_Combined.json'

with open(INPUT_FILE, encoding='utf-8') as f:
    data = json.load(f)

seq = data['sequence']

# Current structure after BUG#1 fix:
# seq[0] = session
# seq[1] = router
# seq[2] = if(Safety Net) { true: [...break], false: [flowSwitch, filter1..5] }

assert len(seq) == 3, f"Expected 3 top-level items, got {len(seq)}"
safety_net = seq[2]
assert safety_net['type'] == 'if', f"Expected 'if', got '{safety_net['type']}'"

false_branch = safety_net['branches']['false']
assert len(false_branch) == 6, f"Expected 6 items in false branch, got {len(false_branch)}"

# Extract flowSwitch and filters from false branch
flow_switch = false_branch[0]
filters = false_branch[1:]

assert flow_switch['type'] == 'flowSwitch', f"Expected flowSwitch, got {flow_switch['type']}"
assert all(f['type'] == 'botReplyFilter' for f in filters), "Not all are botReplyFilter"

# Restore empty false branch (standard pattern for top-level Safety Net)
safety_net['branches']['false'] = []

# Put flowSwitch and filters back at top-level
data['sequence'] = [seq[0], seq[1], seq[2], flow_switch] + filters

print(f"Top-level sequence now has {len(data['sequence'])} items:")
for i, s in enumerate(data['sequence']):
    print(f"  [{i}] {s.get('type')}: {s.get('name')}")

# Save
with open(INPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nDone! flowSwitch restored to top-level.")
print("Safety Net false branch is now [] (standard pattern)")
