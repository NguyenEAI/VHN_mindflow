const fs = require("fs");

const file = "VHN_fixing.json";
const data = JSON.parse(fs.readFileSync(file, "utf8"));

let fixed = false;
for (const node of data.sequence || []) {
  if (node.name === "Flow Switch" && node.type === "flowSwitch" && node.properties?.conditions) {
    node.type = "parallel";
    node.name = "Parallel";
    fixed = true;
  }
}

if (!fixed) {
  throw new Error("No invalid Flow Switch node with conditions was found.");
}

fs.writeFileSync(file, JSON.stringify(data, null, 4), "utf8");
console.log("Route node restored to parallel.");
