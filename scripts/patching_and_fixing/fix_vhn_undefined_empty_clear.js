const fs = require("fs");

const file = "VHN_fixing.json";
const data = JSON.parse(fs.readFileSync(file, "utf8"));

function walk(node) {
  const props = node.properties || {};
  if (
    node.type === "setVar" &&
    (props.varName === "session.extra.product_wishlist" ||
      props.varName === "session.extra.product_information") &&
    props.varValue === "empty_str()"
  ) {
    props.varValue = '""';
  }

  (node.sequence || []).forEach(walk);
  for (const branch of Object.values(node.branches || {})) {
    (branch || []).forEach(walk);
  }
}

data.sequence.forEach(walk);

// The greeting path should stay as simple as possible: just send text.
// Clearing product context on a first greeting is unnecessary and was the only
// new expression-heavy work in the path that produced the undefined error.
const routeNode = data.sequence.find((node) => node.name === "Parallel" && node.branches?.greetings);
if (routeNode) {
  routeNode.branches.greetings = routeNode.branches.greetings.filter(
    (node) =>
      !(
        node.type === "setVar" &&
        (node.properties?.varName === "session.extra.product_wishlist" ||
          node.properties?.varName === "session.extra.product_information")
      ) && node.type !== "sessionSave"
  );
}

fs.writeFileSync(file, JSON.stringify(data, null, 4), "utf8");
console.log("Replaced empty_str clear values and simplified greeting branch.");
