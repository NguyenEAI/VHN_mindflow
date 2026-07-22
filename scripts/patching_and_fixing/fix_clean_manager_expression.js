const fs = require("fs");

const data = JSON.parse(fs.readFileSync("VHN_fixing.json", "utf8"));

function walk(node) {
  if (node.name === "Clean manager JSON") {
    node.properties.expression = `MANAGER = """{{sales_manager}}"""
MANAGER = MANAGER.strip()
if MANAGER.startswith('\`\`\`json'):
    MANAGER = MANAGER[7:]
elif MANAGER.startswith('\`\`\`'):
    MANAGER = MANAGER[3:]
if MANAGER.endswith('\`\`\`'):
    MANAGER = MANAGER[:-3]
print(MANAGER.strip())`;
  }
  (node.sequence || []).forEach(walk);
  for (const branch of Object.values(node.branches || {})) {
    (branch || []).forEach(walk);
  }
}

data.sequence.forEach(walk);
fs.writeFileSync("VHN_fixing.json", JSON.stringify(data, null, 4), "utf8");
console.log("Clean manager expression fixed.");
