const fs = require("fs");

const file = "VHN_fixing.json";
const data = JSON.parse(fs.readFileSync(file, "utf8"));

let idCounter = 0;
function id(prefix) {
  idCounter += 1;
  return `${prefix}_${Date.now()}_${idCounter}`;
}

function walk(node, fn, path = "") {
  fn(node, path);
  (node.sequence || []).forEach((child, index) => walk(child, fn, `${path}.sequence[${index}]`));
  for (const [branchName, branch] of Object.entries(node.branches || {})) {
    (branch || []).forEach((child, index) => walk(child, fn, `${path}.branches[${branchName}][${index}]`));
  }
}

function findNodeByName(name) {
  let found = null;
  data.sequence.forEach((node, index) => {
    walk(node, (item, path) => {
      if (!found && item.name === name) found = { node: item, path: `sequence[${index}]${path}` };
    });
  });
  return found && found.node;
}

function clearProductTasks() {
  return [
    {
      id: id("clear_product_wishlist"),
      type: "setVar",
      componentType: "task",
      properties: {
        varName: "session.extra.product_wishlist",
        varValue: "empty_str()",
      },
      name: "Clear session.extra.product_wishlist",
    },
    {
      id: id("clear_product_information"),
      type: "setVar",
      componentType: "task",
      properties: {
        varName: "session.extra.product_information",
        varValue: "empty_str()",
      },
      name: "Clear session.extra.product_information",
    },
    {
      id: id("save_after_clear_product_context"),
      type: "sessionSave",
      componentType: "task",
      properties: {},
      name: "Save session after clearing product context",
    },
  ];
}

function removeProductInformationBlock(instruction) {
  let next = instruction;
  next = next.replace(
    /\n## Product List \(SOURCE OF TRUTH\)\nASSISTANT MUST ONLY recommend and pull data from the following verified list\.[\s\S]*?"""\n\n/g,
    "\n"
  );
  next = next.replace(/ OR PRODUCT LIST ABOVE/g, "");
  next = next.replace(/ or Product List above/g, "");
  next = next.replace(/ hoặc Product List above/g, "");
  next = next.replace(/Product List above/g, "verified context");
  return next;
}

const managerPrompt = `# ROLE
Bạn là Sales Router của {{ company_name }}. Nhiệm vụ duy nhất: đọc tin nhắn mới nhất và trạng thái trước đó để chọn đúng phase xử lý. KHÔNG tư vấn dài, KHÔNG trả lời khách.

# INPUT
Previous decision: """{{session.extra.previous_manager_decision}}"""
Today: {{ date_time_gmt7 }}

# OUTPUT
Chỉ trả JSON hợp lệ, không markdown/code fence, đủ các field sau: phase, need_product_info, customer_class, current_step, customer_name, customer_phone, user_context, target_product, note_for_sales.

# ENUM
phase chỉ được chọn một trong: greetings, qna, agency_gather_info, gather_requirement, recommend_product, handover, off_topic, thank_you.
need_product_info chỉ được yes hoặc no.
customer_class chỉ được agency, retail hoặc personal. Nếu chưa rõ, mặc định retail.
note_for_sales chỉ được none, spa, clinic, aesthetic, hospital, pharmacy.

# ROUTING RULES
- greetings: chào hỏi, mở đầu, khách chưa nêu nhu cầu rõ.
- qna: hỏi về công ty, chính sách, địa chỉ, phác đồ/liệu trình, xử trí kỹ thuật, thông tin chung không cần lấy data sản phẩm.
- recommend_product: user hỏi tên sản phẩm cụ thể, brand, giá, ảnh, link, thành phần, công dụng, cách dùng, hoặc yêu cầu đề xuất sản phẩm. Khi chọn phase này thì need_product_info = yes.
- gather_requirement: khách lẻ có vấn đề da/nhu cầu nhưng chưa đủ dữ kiện để đề xuất sản phẩm. Hỏi thêm 1-2 ý quan trọng.
- agency_gather_info: khách là spa/phòng khám/thẩm mỹ viện/bệnh viện/nhà thuốc hoặc hỏi mua sỉ/đại lý, cần khai thác thông tin cơ sở.
- handover: cá nhân bán sỉ, phàn nàn nghiêm trọng, muốn gặp người thật, hỏi vấn đề nhạy cảm chưa có dữ liệu xác thực như phụ nữ có thai/cho con bú, check date/giao gấp.
- thank_you: cảm ơn, kết thúc, muốn mua hàng/chốt mua. Hướng sang link Shopee nếu cần.
- off_topic: ngoài phạm vi VHN, viết code, làm thơ, nội dung không liên quan.

# PRODUCT INTENT HEURISTIC
Không cần đọc catalog đầy đủ. Nếu tin nhắn có dấu hiệu hỏi sản phẩm như serum, kem dưỡng, sữa rửa mặt, toner, chống nắng, peel, mask, trị mụn, trị nám, phục hồi, brand Christina/Floslek/Ivatherm/Dermoaroma/Pharmalife/Preime hoặc tên sản phẩm nước ngoài thì chọn recommend_product và need_product_info = yes.

# CONTEXT FIELDS
target_product: mô tả ngắn sản phẩm/nhu cầu cần tìm.
user_context: tóm tắt ngắn loại da, vấn đề da, nhu cầu, khách đang dùng gì nếu có.
current_step: bước tiếp theo nên làm, tối đa 1 câu ngắn.

# CONSTRAINTS
Không tạo phase mới. Không tự bịa thông tin tài chính, giá, link, tồn kho. Nếu không chắc, chọn qna hoặc handover tùy mức độ rủi ro.`;

const managerBlock = findNodeByName("MANAGER");
if (!managerBlock) throw new Error("MANAGER block not found");
const managerSeq = managerBlock.sequence || [];
const managerQnaIndex = managerSeq.findIndex((node) => node.name === "GPT-4 MANAGER");
const managerPythonIndex = managerSeq.findIndex((node) => node.name === "Python");
const managerIf = managerSeq.find((node) => node.name === "verify_manager_decision_format");
if (managerQnaIndex === -1 || managerPythonIndex === -1 || !managerIf) {
  throw new Error("MANAGER internal nodes not found");
}

const managerQna = managerSeq[managerQnaIndex];
Object.assign(managerQna.properties, {
  instruction: managerPrompt,
  llm_alt_model: "gpt-4o-mini",
  chat_history_aware: false,
  human_input_aware: true,
  max_tokens: "500",
  temperature: "0.2",
});

const cleanManagerNode = {
  id: id("clean_manager_json"),
  type: "python",
  componentType: "task",
  properties: {
    varName: "sales_manager_clean",
    expression: `MANAGER = """{{sales_manager}}"""
MANAGER = MANAGER.strip()
if MANAGER.startswith("""" + "\`\`\`json" + """"):
    MANAGER = MANAGER[7:]
elif MANAGER.startswith("""" + "\`\`\`" + """"):
    MANAGER = MANAGER[3:]
if MANAGER.endswith("""" + "\`\`\`" + """"):
    MANAGER = MANAGER[:-3]
print(MANAGER.strip())`,
  },
  name: "Clean manager JSON",
};

managerSeq.splice(managerPythonIndex, 0, cleanManagerNode);
const verifyNode = managerSeq.find((node) => node.name === "Python");
verifyNode.properties.expression = `import json

MANAGER = """{{sales_manager_clean}}"""
MANAGER = MANAGER.strip()

KEYS = ["phase", "need_product_info", "customer_class", "current_step", "customer_name", "customer_phone", "user_context", "target_product", "note_for_sales"]
PHASES = ["greetings", "qna", "agency_gather_info", "gather_requirement", "recommend_product", "handover", "off_topic", "thank_you"]
NOTES = ["none", "spa", "clinic", "aesthetic", "hospital", "pharmacy"]
CLASS = ["agency", "retail", "personal"]

try:
    parsed_data = json.loads(MANAGER)
    phase_value = parsed_data.get("phase", "") or ""
    note_value = parsed_data.get("note_for_sales", "") or ""
    class_value = parsed_data.get("customer_class", "") or ""
    result_phase = any(key == phase_value for key in PHASES)
    result_note = any(key == note_value for key in NOTES)
    result_class = any(key == class_value for key in CLASS)
    missing_keys = [k for k in KEYS if k not in parsed_data]
    print("Yes" if not missing_keys and result_phase and result_note and result_class else "No")
except Exception:
    print("No")`;
for (const child of managerIf.branches.true || []) {
  if (child.type === "setVar" && child.properties.varValue === "json.loads(sales_manager)") {
    child.properties.varValue = "json.loads(sales_manager_clean)";
  }
}

// Safer recall properties.
data.sequence.forEach((node) => {
  walk(node, (item) => {
    if (item.type === "recall") item.properties = {};
  });
});

// Safer attachment condition: compute a simple flag first, avoid `!=` in condition.
const attachmentIfIndex = data.sequence.findIndex((node) => node.name === "If attachments");
if (attachmentIfIndex !== -1) {
  data.sequence.splice(attachmentIfIndex, 0, {
    id: id("check_attachment"),
    type: "python",
    componentType: "task",
    properties: {
      varName: "has_attachment",
      expression: `try:
    print("yes" if attachments else "no")
except Exception:
    print("no")`,
    },
    name: "Check attachments",
  });
  data.sequence[attachmentIfIndex + 1].properties.condition = 'has_attachment == "yes"';
}

// Product API: pass vendor from extracted query when JSON is valid.
data.sequence.forEach((node) => {
  walk(node, (item) => {
    if (item.name === "API CALL PRODUCT DATA" && item.properties && item.properties.api_body) {
      if (item.properties.api_body.includes('"product_type": "{{ session.extra.query_data.product_type }}"')) {
        item.properties.api_body = item.properties.api_body.replace(
          '"vendor": "none"',
          '"vendor": "{{ session.extra.query_data.vendor }}"'
        );
      }
    }
  });
});

// Limit product payload before formatting wishlist/final product information.
data.sequence.forEach((node) => {
  walk(node, (item) => {
    if (item.type === "python" && item.properties && item.properties.expression) {
      let expr = item.properties.expression;
      if (expr.includes("PRODUCTS = {{api_raw_product_data[0].data}}") && !expr.includes("PRODUCTS = PRODUCTS[:8]")) {
        expr = expr.replace(
          "PRODUCTS = {{api_raw_product_data[0].data}}",
          "PRODUCTS = {{api_raw_product_data[0].data}}\nPRODUCTS = PRODUCTS[:8]"
        );
      }
      item.properties.expression = expr;
    }
  });
});

// Remove product_information from non-product final nodes.
for (const nodeName of ["GPT-4o Mini QnA", "GPT-4 Gather Requirement"]) {
  const node = findNodeByName(nodeName);
  if (node && node.properties && node.properties.instruction) {
    node.properties.instruction = removeProductInformationBlock(node.properties.instruction);
  }
}

// Reduce aware flags / max tokens where full context is not needed.
const config = {
  "GPT-4 Query Data": { chat_history_aware: false, max_tokens: "500", temperature: "0.2" },
  "GPT-4 Analysis": { chat_history_aware: false, max_tokens: "500", temperature: "0.2" },
  "GPT-4o Mini Offtopic": { chat_history_aware: false, max_tokens: "500" },
  "GPT-4o Mini Thank you": { chat_history_aware: false, max_tokens: "300" },
  "GPT-4o Mini Handover": { chat_history_aware: false, max_tokens: "300" },
};
data.sequence.forEach((node) => {
  walk(node, (item) => {
    if (item.type === "qna" && config[item.name]) Object.assign(item.properties, config[item.name]);
  });
});

// Replace greeting LLM branch with a static greeting.
const parallelNode = data.sequence.find((node) => node.name === "Parallel");
if (!parallelNode) throw new Error("Parallel node not found");
parallelNode.type = "flowSwitch";
parallelNode.name = "Flow Switch";
if (parallelNode.branches && parallelNode.branches.greetings) {
  parallelNode.branches.greetings = [
    {
      id: id("static_greeting"),
      type: "botSendText",
      componentType: "task",
      properties: {
        text: "Dạ em chào Anh/Chị, em là Thảo Vi từ Y Dược VHN. Anh/Chị đang quan tâm sản phẩm nào hoặc cần em hỗ trợ vấn đề gì ạ?",
      },
      name: "Bot Send Text Greeting",
    },
    ...clearProductTasks(),
  ];
}

// Clear product context after every final branch response so stale product text cannot leak into later turns.
for (const [branchName, branch] of Object.entries(parallelNode.branches || {})) {
  if (branchName === "greetings") continue;
  const hasClear = branch.some((node) => node.name === "Clear session.extra.product_information");
  if (!hasClear) branch.push(...clearProductTasks());
}

fs.writeFileSync(file, JSON.stringify(data, null, 4), "utf8");
console.log("Applied VHN token fixes.");
