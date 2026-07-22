---
name: conductify-mindflow-vhn
description: Hướng dẫn xây dựng và debug AI Sales Agent trên Conductify AI Studio (Mindflow Raw JSON) cho Y Dược VHN và các dự án tương tự. Dùng khi cần tạo flow mới, fix lỗi Exception parser, restructure flow, hoặc tinh chỉnh prompt order/consult. Tham chiếu gold-standard từ Shegan AI Sales Agent.
---

# Conductify Mindflow Builder — Bộ quy tắc & Bug-fix Playbook

## 1. CẤU TRÚC TOP-LEVEL CHUẨN (KHỚP SHEGAN — PHẢI THEO ĐÚNG THỨ TỰ)

```
sequence: [
  0. session          (Session Manager — khởi tạo extra vars)
  1. router           (Phân loại topic từ tin nhắn)
  2. if               (Safety Net: recall_counter > 3)
  3. flowSwitch       (Phân nhánh 10 flow theo topic)
  4-N. botReplyFilter (Lọc xưng hô top-level — KHÔNG đặt trong flow)
]
```

**SAI THỨ TỰ = sai logic.** Router phải đứng TRƯỚC Safety Net vì Safety Net chỉ ý nghĩa sau khi đã có topic.

## 2. RULE VÀNG VỀ flowSwitch

- **CHỈ DÙNG 1 flowSwitch ở TOP-LEVEL** để route 10 topic.
- **TUYỆT ĐỐI KHÔNG nested flowSwitch** trong flow. Conductify auto-template generator KHÔNG hỗ trợ → sinh template không cân đối → parser lỗi `Expected end of text, found '{'`.
- Branching trong flow → dùng `type: if` lồng nhau (Shegan place_order có 5+ tầng `if` lồng, chạy ổn).

### Chuyển nested flowSwitch → if-else chain

Với flowSwitch có N branches có conditions A,B,C,D:
```
if (cond_A): branch_A
else:
  if (cond_B): branch_B
  else:
    if (cond_C): branch_C
    else: branch_D  ← branch cuối làm default
```

## 3. GIỚI HẠN CONDITION SYNTAX (CRITICAL — DỄ GÂY LỖI NHẤT)

### 3.1. Conductify CHỈ hỗ trợ condition đơn giản

| Hỗ trợ | Ví dụ |
|---|---|
| So sánh `==` đơn | `order_info.action == "EXIT"` |
| Chuỗi `or` đơn giản | `topic == "a" or topic == "b" or topic == "c"` |
| Dot-access biến | `order_info.action == "EXIT"`, `confirm_info.decision == "yes"` |

| **KHÔNG HỖ TRỢ** | Ví dụ SAI |
|---|---|
| `and` | `action == "EXIT" and product != ""` |
| `!=` | `product_requirement != "NOT-PROVIDED"` |
| Ngoặc `()` | `(a == "x" or b == "y")` |
| Kết hợp `and` + `or` | `a == "x" and (b == "y" or b == "z")` |
| **`{{var}}` placeholder trong condition** | `{{order_check}} == "NO"` ← gây parser crash |

**Vi phạm → `Error in Prompt Program: list index out of range`** — Conductify template generator crash, KHÔNG phải lỗi logic.

### 3.1.1. CRITICAL — KHÔNG dùng `{{var}}` trong field `condition`

Khi engine compile `{{#if ...}}`, nó nhét nguyên nội dung condition vào. Nếu condition chứa `{{order_check}}` (có ngoặc kép), engine tạo ra template lồng `{{#if {{order_check}} == "NO" }}`, parser tưởng đã đóng block sớm rồi gặp `{` không mong đợi → **`Expected end of text, found '{' at char XXXXX`**.

```json
// SAI — gây crash:
"condition": "{{order_check}} == \"NO\""

// ĐÚNG — dùng tên biến trực tiếp:
"condition": "order_check == \"NO\""
"condition": "order_info.action == \"EXIT\""
"condition": "confirm_info.decision == \"yes\""
```

**Quy tắc**: trong field `condition` (và bất kỳ field `conditions/*`, `varName`) → luôn dùng raw variable name, KHÔNG bao giờ wrap bằng `{{...}}`. Chỉ field `text` / `instruction` mới được dùng `{{...}}`.

### 3.2. Giải pháp thay thế cho logic phức tạp

Thay vì dùng condition phức tạp, **tách thành nhiều tầng if đơn giản lồng nhau**:

```
# SAI — dùng `and` + `!=`:
IF action == "EXIT" and product_requirement != "NOT-PROVIDED"

# ĐÚNG — tách 2 tầng, mỗi tầng chỉ dùng `==`:
IF action == "EXIT"
  TRUE:
    IF product_requirement == "NOT-PROVIDED"
      TRUE: [thực sự exit]
      FALSE: [guard — user chỉ bỏ bớt SP, không exit thật]
  FALSE: ...
```

### 3.3. Giới hạn nesting: tối đa ~3 tầng if

Conductify hỗ trợ khoảng 3 tầng if lồng nhau. Vượt quá có thể gây lỗi template. Nếu logic cần > 3 tầng → đẩy logic vào AI prompt (json_mode) rồi dùng if-chain đơn giản route output.

## 4. RULE VÀNG VỀ clearTopic

- `clearTopic` block hoạt động ĐÚNG khi nằm TRONG flow (sau qna/botSendText).
- **TUYỆT ĐỐI KHÔNG dùng `clearTopic` trực tiếp trong top-level `if`** (Safety Net). Thay bằng:
  ```json
  {
    "type": "setVar",
    "properties": { "varName": "topic", "varValue": "json.dumps(session)" }
  }
  ```

## 5. RULE VỀ `{{#if}}` TRONG botSendText

- **KHÔNG dùng `{{#if}}` conditional** bên trong trường `text` của `botSendText`. Có thể gây crash template generator của Conductify.
- Nếu cần hiển thị nội dung có điều kiện → tách thành nhiều `botSendText` block với if-block Mindflow bên ngoài.

## 6. PATTERN FLOW THEO ĐỘ PHỨC TẠP

### 6.1. Simple flow (greetings, off_topic, promotion, brand_info, company_info, internal_staff)
```
[qna] AI QnA
[clearTopic]
```
KHÔNG có saveHumanInput. KHÔNG có if-block.

### 6.2. Handover flow
```
[qna] AI Analyze (json_mode, varReply=handover_analyze)
[setVar] handover
[botSendText] Thông báo chuyển tiếp (thay botAPICall nếu chưa có API thật)
[qna] AI Reply
[clearTopic]
```

### 6.3. Consult flow (b2c_consult, b2b_consult)
```
[saveHumanInput]
[qna] AI Tư vấn chính (varReply=bot_xxx_reply)
[python] Save chat_history_xxx vào session.extra
[qna] AI Extract Product (b2c) hoặc Lead Info (b2b)
[setVar] Save extracted data
[sessionSave]
[qna] AI Check Status (json_mode → status: READY/CONTINUE/EXIT)
[setVar] Set status
[if] If status == READY:
  true: botSendText + clearTopic
  false:
    if status == EXIT:
      true: botSendText + clearTopic
      false: botSendText reply (default = CONTINUE)
```

### 6.3.1. ANTI-PATTERN: Nested if trong topic branch (CRITICAL)

Engine có quirk khi compile topic branch chứa **nested `if`**. Cứ mỗi level nested if là +1 `{{/if}}` ở cuối. Tổng số `{{/if}}` chồng nhau ở cuối branch làm parser tưởng đã hết template, gặp `{{#if topic == "..."}}` kế tiếp thì báo **`Expected end of text, found '{'`**.

Các branch KHÔNG có nested if đều OK. Các branch có nested if đều crash → phải refactor thành **flat structure với 1 `flowSwitch` cuối nhánh** (giống pattern b2c_consult/b2b_consult đã chạy được).

**SAI — nested if:**
```
order:
  [saveHumanInput, qna, setVar,
   if status == EXIT:
     true: [exit_msg, clearTopic]
     false:
       if order_check == NO:
         true: [ask missing]
         false:
           if confirm == yes: [API, success]
           else: [ask again]
  ]
```

**ĐÚNG — flat với flowSwitch:**
```
order:
  saveHumanInput
  qna "AI Decide Order Action" → JSON {action, customer_info, reply_text}
  setVar order_info
  python collect chat history
  sessionSave
  flowSwitch on order_info.action:
    exit_order:       sendText(reply_text) + clear histories + clearTopic
    incomplete_order: sendText(reply_text)
    confirm_needed:   sendText(reply_text)
    confirmed_order:  API call + success msg + save + clearTopic
```

AI làm 1 lần cả parse + quyết định action + sinh reply_text. flowSwitch chỉ route action ra các nhánh phẳng. **Tất cả 10 topic branches nên có `ifs=0`**, chỉ dùng `flowSwitch` ở cuối nhánh nếu cần route.

### 6.3.2. ANTI-PATTERN: empty `false: []` + task sibling sau đó

```
[saveHumanInput, qna, setVar, IF(empty false), python, IF(...)]
                                ↑ if với false:[] rồi có TASK SIBLING ngay sau
```

Engine compile pattern này sinh `{{/if}}` thừa → khi sang topic kế tiếp parser báo `Expected end of text`.

**Fix**: Gom toàn bộ logic continuation vào TRONG `false` branch của if đầu (đừng để task sibling sau if với false rỗng).

### 6.4. Order flow (phức tạp nhất — CẤU TRÚC MỚI VỚI STRUCTURAL GUARD)

```
[saveHumanInput]
[qna] AI Decide Order Action (json_mode → xem section 7 chi tiết)
[setVar] order_info
[python] Collect Register Chat History
[sessionSave]
[if] action == "EXIT"                          ← Tầng 1
  TRUE:
    [if] product_requirement == "NOT-PROVIDED"  ← Tầng 2a (Guard)
      TRUE:
        botSendText Goodbye
        setVar clear registration_chat_history
        sessionSave
        setVar clear findproduct_data
        clearTopic                              ← Chỉ EXIT thật khi product = NOT-PROVIDED
      FALSE:
        botSendText "Em đã cập nhật đơn hàng: [remaining products]..."
                                                ← Guard: user bỏ bớt SP, KHÔNG exit
  FALSE:
    [if] action == "CONFIRMED"                  ← Tầng 2b
      TRUE:
        [if] customer_phone == "NOT-PROVIDED"   ← Tầng 3 (Missing info guard)
          TRUE:
            botSendText "Anh/Chị vui lòng cung cấp SĐT và địa chỉ..."
          FALSE:
            botSendText Order Success
            python Save old_order_customer_information
            setVar Clear registration_chat_history
            sessionSave
            setVar Clear findproduct_data
            clearTopic
      FALSE:
        botSendText reply_text                  ← Handles INCOMPLETE + CONFIRM_NEEDED
```

**QUAN TRỌNG VỀ STRUCTURAL GUARD:**

gpt-4o-mini KHÔNG đủ khả năng phân biệt chính xác giữa "bỏ bớt SP" (remove some) và "hủy đơn" (cancel all) chỉ bằng instruction. Khi user nói "thôi bỏ kem chống nắng đi" (chỉ bỏ 1 SP), AI thường đặt `action = EXIT` dù vẫn còn SP khác.

**Giải pháp**: Structural guard ở Mindflow level — nếu `action == EXIT` nhưng `product_requirement != NOT-PROVIDED` (tức vẫn còn SP), thì KHÔNG exit mà tiếp tục flow với danh sách SP còn lại.

Quy tắc trong AI prompt: Khi `action = EXIT`, PHẢI set `product_requirement = "NOT-PROVIDED"`. Nếu AI đặt EXIT nhưng vẫn ghi SP → guard bắt và tiếp tục.

**LƯU Ý VỀ botAPICall:**
- `botAPICall` yêu cầu URL thật. Nếu chưa có API endpoint → dùng `botSendText` hiển thị thông tin xác nhận đơn thay thế (MVP approach).
- Khi có API thật, thay `botSendText` Order Success bằng `botAPICall` + `botSendText`.

## 7. AI PROMPT ORDER — CẤU TRÚC 3 BƯỚC BẮT BUỘC

### 7.1. Quy trình 3 bước trong AI Decide Order Action

```
BƯỚC 1: KIỂM TRA ĐIỀU CHỈNH ĐƠN HÀNG
- User có đang THÊM/BỎ/ĐỔI sản phẩm không?
- "Bỏ X đi", "Không lấy X nữa", "Thêm Y vào" → ĐIỀU CHỈNH, KHÔNG PHẢI EXIT
- Chỉ khi bỏ hết ALL sản phẩm mới là EXIT

BƯỚC 2: KIỂM TRA 4 TRƯỜNG BẮT BUỘC
- customer_name: tên khách
- customer_phone: SĐT
- customer_address: địa chỉ giao hàng
- product_requirement: danh sách SP
- Nếu missing_count >= 1 → action PHẢI là INCOMPLETE

BƯỚC 3: CHỌN ACTION
- EXIT: user muốn HỦY HOÀN TOÀN đơn / kết thúc
- INCOMPLETE: còn thiếu thông tin bắt buộc
- CONFIRM_NEEDED: đủ info, cần xác nhận
- CONFIRMED: user đã xác nhận rõ ràng (VD: "ok đặt đi", "xác nhận")
```

### 7.2. Few-shot examples (tiếng Việt — BẮT BUỘC trong prompt)

```
VD1: "Thôi bỏ kem chống nắng đi em" (đang có 2 SP)
→ ĐIỀU CHỈNH, KHÔNG phải EXIT
→ product_requirement = "[SP còn lại]", action = "CONFIRM_NEEDED"

VD2: "Thôi em không mua nữa đâu"
→ EXIT thật, product_requirement = "NOT-PROVIDED"

VD3: "Bỏ hết đi em, anh không lấy nữa"
→ EXIT thật, product_requirement = "NOT-PROVIDED"

VD4: "Bỏ kem chống nắng, lấy thêm sữa rửa mặt"
→ ĐIỀU CHỈNH, action = "CONFIRM_NEEDED"

VD5: "Bỏ thêm cho anh kem chống nắng nữa nha em" (đang có 2 SP)
→ "bỏ thêm" = "additionally remove" = XÓA THÊM (KHÔNG phải add)
→ ĐIỀU CHỈNH (remove), action = "CONFIRM_NEEDED"
→ product_requirement chỉ còn SP còn lại

VD6: "Tư vấn cho anh thêm 1 sản phẩm toner cho da của anh đi bé" (đang có 1 SP trong đơn)
→ Đây là YÊU CẦU TƯ VẤN, KHÔNG phải đặt thêm SP vào đơn
→ action = "EXIT" (rời khỏi luồng order, sang luồng tư vấn)
→ product_requirement = GIỮ NGUYÊN đơn cũ (KHÔNG xóa!) — KHÔNG set NOT-PROVIDED
→ reply_text = câu hướng dẫn AI sẽ tư vấn toner phù hợp
```

### 7.2.1. CRITICAL — Phân biệt "bỏ thêm" vs "thêm vào"

Từ "thêm" trong tiếng Việt có 2 nghĩa khác nhau hoàn toàn:
- **"bỏ thêm X" / "bỏ X nữa" / "bỏ luôn X"** = additionally remove = **XÓA THÊM X khỏi đơn**
- **"thêm X vào" / "lấy thêm X" / "đặt thêm X"** = add = **THÊM X vào đơn**

PHẢI dạy AI rõ trong instruction: từ "thêm" sau động từ "bỏ" luôn nghĩa là "additionally" (xóa thêm), KHÔNG phải "add".

### 7.2.2. CRITICAL — Phân biệt "tư vấn thêm SP" vs "đặt thêm SP"

- **"tư vấn cho anh thêm sản phẩm X"** = REQUEST TƯ VẤN → action=EXIT nhưng **GIỮ ĐƠN CŨ** (KHÔNG xóa product_requirement). Sau đó Mindflow phải `clearTopic` để Router phân lại sang luồng tư vấn.
- **"lấy thêm sản phẩm X" / "đặt thêm X"** = ADD TO ORDER → ĐIỀU CHỈNH, CONFIRM_NEEDED, thêm X vào product_requirement.

Pattern flow cho case "tư vấn thêm":
```
EXIT branch:
  IF product_requirement == "NOT-PROVIDED" → exit thật (hủy đơn)
  ELSE → vẫn còn đơn cũ → botSendText reply_text + clearTopic
                          (lượt sau Router phân sang b2c_consult tư vấn tiếp)
```

### 7.3. JSON output schema cho Order QnA

```json
{
  "action": "EXIT | INCOMPLETE | CONFIRM_NEEDED | CONFIRMED",
  "customer_name": "tên KH hoặc NOT-PROVIDED",
  "customer_phone": "SĐT hoặc NOT-PROVIDED",
  "customer_address": "địa chỉ hoặc NOT-PROVIDED",
  "product_requirement": "SP1 (xSL, GIÁ) ; SP2 (xSL, GIÁ) hoặc NOT-PROVIDED",
  "shipping_fee": "MIỄN PHÍ hoặc 30,000 VNĐ",
  "total_price": "X VNĐ hoặc LIÊN HỆ",
  "payment_method": "COD hoặc Chuyển khoản ngân hàng",
  "reply_text": "Nội dung phản hồi cho user"
}
```

### 7.4. Quy tắc EXIT bắt buộc

Khi `action = EXIT` → **PHẢI** set `product_requirement = "NOT-PROVIDED"`. Đây là tín hiệu cho structural guard trong Mindflow. Nếu AI set EXIT nhưng vẫn ghi SP → guard phát hiện và tiếp tục flow thay vì exit.

## 8. AI PROMPT — RULES BẮT BUỘC KHÁC

### 8.1. AI trả JSON: phải ép kiểu CHUỖI, không phải list
SAI:
```
product_requirement: [{"product_name": "...", "quantity": 1}]
```
ĐÚNG (ép trong prompt):
```
product_requirement: CHUỖI duy nhất, mỗi SP cách nhau bằng ' ; '
VD: "Floslek Anti Acne (x1, 650,000 VNĐ) ; Christina Unstress (x1, 1,200,000 VNĐ)"
TUYỆT ĐỐI KHÔNG trả về mảng/object.
```

### 8.2. Field giá tiền — luôn dạng chuỗi có dấu phẩy + VNĐ
```
total_price: CHUỖI, VD "1,850,000 VNĐ"
Nếu không xác định được giá → "LIÊN HỆ"
```

### 8.3. AI Extract Product (b2c_consult) — luôn lấy KÈM GIÁ
Format ép buộc:
```
<Tên SP> | <giá VNĐ hoặc 'LIÊN HỆ'>
VD:
Floslek Anti Acne | 650,000 VNĐ
Christina Unstress | 1,200,000 VNĐ
```

## 9. CHÍNH SÁCH SHIPPING & THANH TOÁN

### 9.1. Shipping policy (tích hợp trong Session Manager extra vars)

```json
{
  "shipping_policy": "Đơn hàng từ 1,000,000 VNĐ trở lên: MIỄN PHÍ vận chuyển. Đơn hàng dưới 1,000,000 VNĐ: phí vận chuyển 30,000 VNĐ. Áp dụng toàn quốc.",
  "shipping_fee_threshold": "1000000",
  "shipping_fee_amount": "30000"
}
```

### 9.2. Hình thức thanh toán

- **COD** (thanh toán khi nhận hàng) — mặc định
- **Chuyển khoản ngân hàng**

Phải tích hợp vào:
- Session Manager extra vars
- Order QnA instruction (AI phải hỏi và ghi nhận phương thức thanh toán)
- Order Success message (hiển thị phương thức đã chọn)
- Promotion flow (nếu mention shipping/payment)
- Company Info flow (thông tin chung về chính sách)

### 9.3. Router phrases cho shipping/payment

Thêm vào Router các cụm từ trigger:
- `"phí ship bao nhiêu"`, `"có miễn phí vận chuyển không"`
- `"thanh toán bằng cách nào"`, `"có chuyển khoản được không"`, `"thanh toán chuyển khoản"`

## 10. GUARDRAILS QUAN TRỌNG (cho prompt tư vấn)

Luôn nhúng vào instruction của AI QnA tư vấn:
- **CHỈ đề xuất SP đúng loại**: B2C flow chỉ dùng `is_salon_product=False`, B2B chỉ dùng `is_salon_product=True`.
- **KHÔNG báo giá sỉ** cho B2B qua chat → xin SĐT để chuyên viên KD liên hệ.
- **SP thiếu giá**: "Dạ, sản phẩm ... đang có chương trình ưu đãi đặc biệt... vui lòng để lại SĐT để em báo giá chính xác kèm quà tặng..."
- **Xưng hô**: "em" / "Anh/Chị" / "Dạ". KHÔNG xưng "tôi", "mình", KHÔNG nói "tôi là AI/bot/chatbot".

## 11. ROUTER PHRASE LOGIC

Phrases trong Router phải SPECIFIC để route đúng intent:
- `order` topic: KHÔNG bao gồm cụm "đặt thêm/lấy thêm/mua thêm" — đó là intent TƯ VẤN THÊM.
- `b2c_consult` topic: thêm "còn sản phẩm nào", "tư vấn thêm", "đề xuất thêm", "đặt thêm sản phẩm".
- `internal_staff` topic: thêm phrases như "liệt kê SP key", "thống kê SP theo vendor", "dòng X có gì".

## 12. SESSION.EXTRA — CÁC BIẾN CHUẨN PHẢI KHỞI TẠO

```json
{
  "customer_type": "", "customer_name": "", "customer_phone": "", "customer_address": "",
  "facility_name": "", "facility_type": "",
  "skin_type": "", "skin_concern": "", "age_range": "",
  "employee_authenticated": "no",
  "chat_history_b2b": "", "chat_history_b2c": "",
  "registration_chat_history": "",
  "findproduct_data": "",
  "old_order_customer_information": "NA",
  "assistant_role": "...", "assistant_tone": "...", "vn_pronoun": "...",
  "company_name": "...", "company_short_name": "...", "company_contact": "...",
  "company_product": "...",
  "shipping_policy": "Đơn hàng từ 1,000,000 VNĐ trở lên: MIỄN PHÍ...",
  "shipping_fee_threshold": "1000000",
  "shipping_fee_amount": "30000",
  "required_fields_for_b2c_order": [...],
  "required_fields_for_b2b_lead": [...],
  "stop_examples": [...],
  "register_successfully": "..."
}
```

## 13. BUG PATTERNS & DEBUG

### 13.1. `Error in Prompt Program: list index out of range`

**Nguyên nhân**: Conductify template generator crash khi gặp condition phức tạp (dùng `and`, `!=`, `()` trong if condition).

**Debug checklist:**
1. Tìm TẤT CẢ condition trong file → kiểm tra có `and`, `!=`, `()` không
2. Thay thế bằng nested if đơn giản (chỉ `==`)
3. Đếm tầng if lồng nhau → phải <= 3

**Đây KHÔNG phải lỗi logic** — là crash của Conductify parser. Dù condition đúng logic vẫn crash nếu syntax phức tạp.

### 13.2. `Expected end of text, found '{'`

**Nguyên nhân**: Template generator sinh cặp `{{}}` không cân đối.

**Debug checklist:**
1. Đếm flowSwitch → phải = 1 (chỉ top-level). Nested flowSwitch → chuyển if-else chain
2. Tìm clearTopic trong top-level if → thay bằng setVar
3. Kiểm tra inner if-block trong simple flow → loại bỏ
4. Kiểm tra branch FALSE rỗng `false: []` → thêm tối thiểu 1 block
5. Check `{{#if}}` trong botSendText text → loại bỏ

### 13.3. Lỗi cache template cũ

**Triệu chứng**: Lỗi cố định cùng char position sau khi đã sửa code.

**Fix**: Re-import hoàn toàn:
1. XÓA SẠCH ô Mindflow Raw
2. Save (trống)
3. Paste JSON mới
4. Save
5. Refresh page (Ctrl+F5)
6. Reset conversation

### 13.4. `recall` task — properties phải RỖNG

**SAI:**
```json
{ "type": "recall", "properties": { "max_loop": "10" } }
```

Property `max_loop` không tồn tại trong engine. Reference `ai_sales_agent.txt` (Shegan) tất cả `recall` đều có `"properties": {}`. Khi compile, engine emit fragment template lệch → gây `Expected end of text, found '{'` ngay khi sang topic kế tiếp.

**ĐÚNG:**
```json
{ "type": "recall", "properties": {} }
```

**Lưu ý thêm**: `recall` render fragment có `{{/block}}` cuối. `{{/block}}` này kéo theo việc close 1 block scope mà cấu trúc engine không cân với phần wrapping (do partial `guidance_program_clone` cần được include trong layout cụ thể). Nếu dùng `recall` ở vị trí sai (không phải "no semantic results" hoặc "user-want-exit") → có thể gây mất cân đối. Khi nghi ngờ → thay `recall` bằng `botSendText` lịch sự hỏi User reply, lượt sau Router phân lại topic.

### 13.5. Multi-line JSON literal trong instruction gây parser issue

**SAI** — instruction chứa block JSON literal multi-line:
```
"instruction": "Trả về JSON như sau:\n{\n  \"product_requirement\": \"...\",\n  \"action\": \"...\"\n}"
```

Parser của Conductify có thể nhầm `{` `}` trong literal là block control → emit template lệch.

**ĐÚNG** — mô tả schema bằng prose:
```
"instruction": "Trả về JSON có các field: product_requirement (chuỗi SP cách nhau bằng ' ; '), action (enum: EXIT/INCOMPLETE/CONFIRM_NEEDED/CONFIRMED), customer_name (chuỗi hoặc 'NOT-PROVIDED'), ..."
```

### 13.6. `session.extra.XXX` not found sau nhiều lượt chat

**Triệu chứng**: Biến `{{ session.extra.shipping_policy }}` hoạt động ở lượt đầu nhưng sau ~10-20 lượt chat thì lỗi "not found".

**Nguyên nhân**: Conductify có giới hạn kích thước `session.extra`. Khi `chat_history_b2c`, `chat_history_b2b`, `registration_chat_history` tích lũy qua nhiều lượt → `session.extra` quá lớn → platform truncate một số biến tĩnh.

**Fix**:
1. **Hardcode thông tin tĩnh** vào prompt thay vì lưu session var:
   - Shipping policy, payment methods, persona — đều là static
   - Chỉ lưu vào session.extra những biến THỰC SỰ thay đổi theo cuộc hội thoại (customer info, cart, employee_authenticated)
2. **Clear chat histories sau order CONFIRMED/EXIT** để giảm size:
   ```
   setVar chat_history_b2c = ""
   setVar registration_chat_history = ""
   setVar findproduct_data = ""
   sessionSave
   ```
3. Áp dụng cho cả nhánh CONFIRMED và EXIT.

### 13.7. `setTopic` component KHÔNG TỒN TẠI

`setTopic` không phải component hợp lệ của Conductify engine. Reference `ai_sales_agent.txt` KHÔNG dùng `setTopic`.

**Để chuyển topic** dùng combo: `botSendText` (hỏi/dẫn dắt) → `clearTopic` → lượt sau Router bắt intent mới và phân topic mới. KHÔNG có cách "force set topic" trực tiếp.

### 13.8. AI BỊA thông tin tài chính (NGHIÊM TRỌNG — risk mất tiền KH)

**Triệu chứng**: AI tự sinh số tài khoản ngân hàng giả ("123456789", "Ngân hàng TMCP ABC"), QR code giả, link thanh toán giả.

**Hậu quả**: Khách chuyển tiền vào tài khoản giả → mất tiền. Rủi ro lớn nhất của AI Sales Agent.

**Fix**: Thêm constraint NGHIÊM NGẶT vào TẤT CẢ flows có thể đụng đến thông tin tài chính:
- **Order flow**: "TUYỆT ĐỐI KHÔNG BỊA số tài khoản, tên ngân hàng, mã QR, link thanh toán. Khi khách chọn 'chuyển khoản' → chỉ set `payment_method = 'Chuyển khoản'` và reply 'Nhân viên VHN sẽ gửi thông tin chuyển khoản khi liên hệ xác nhận đơn'."
- **Company_info flow**: "Nếu User hỏi thông tin chuyển khoản/số TK/QR → hướng dẫn liên hệ hotline [số thật], KHÔNG tự bịa."
- **Promotion flow**: tương tự, KHÔNG bịa số TK/voucher code không có trong knowledge.

Thêm few-shot example trong prompt order:
```
VD: "anh thanh toán bằng chuyển khoản nha"
→ SAI: reply có "Số TK: 123456789, NH ABC" (BỊA!)
→ ĐÚNG: chỉ set payment_method = "Chuyển khoản", reply "Em đã ghi nhận hình thức chuyển khoản. Nhân viên VHN sẽ gửi số tài khoản khi gọi xác nhận đơn ạ."
```

### 13.9. gpt-4o-mini nhận diện sai intent tiếng Việt

**Vấn đề**: gpt-4o-mini không đủ khả năng phân biệt các intent gần nhau trong tiếng Việt chỉ bằng instruction. VD:
- "bỏ kem chống nắng đi" (bỏ 1 SP) vs "thôi không mua nữa" (hủy đơn)
- "bỏ thêm X nữa" (xóa thêm X) vs "thêm X vào" (add X)
- "tư vấn thêm SP toner" (request tư vấn) vs "đặt thêm toner" (add to cart)

**Giải pháp layered**:
1. **Layer 1 — Instruction**: Thêm BƯỚC 1 check điều chỉnh trước EXIT, thêm few-shot examples tiếng Việt CỤ THỂ (xem section 7.2)
2. **Layer 2 — Structural guard**: Dùng if-check trong Mindflow:
   - Nếu `EXIT` nhưng `product != NOT-PROVIDED` → không exit thật (case "bỏ bớt SP" hoặc "tư vấn thêm")
3. **Layer 3 — Phân loại EXIT thành 2 case**:
   - EXIT + product=NOT-PROVIDED → hủy thật (clear all + clearTopic)
   - EXIT + product≠NOT-PROVIDED → có 2 sub-case:
     * User chỉ bỏ bớt SP → tiếp tục order với SP còn lại
     * User muốn tư vấn thêm → reply hướng dẫn + clearTopic (Router phân lại)
4. **Chỉ instruction KHÔNG ĐỦ** — phải luôn có structural guard cho các case nhạy cảm

## 14. TOP-LEVEL botReplyFilter (Đặt SAU Flows Switch)

5 filter regex bắt buộc (top-level, KHÔNG lặp trong từng flow):

| # | regex | replace |
|---|---|---|
| 1 | `(?:Tôi\|tôi)` | `em` |
| 2 | `chúng tôi` | `bên em` |
| 3 | `chatbot\|bot\|AI` | `tư vấn viên` |
| 4 | `bạn` (chuẩn) | `Anh/Chị` |
| 5 | `tôi không biết` | `em chưa có thông tin chi tiết về phần này` |

## 15. MINDFLOW COMPONENTS REFERENCE

| Component | Mô tả | Lưu ý |
|---|---|---|
| `session` | Khởi tạo session, extra vars | Luôn đầu tiên |
| `router` | Phân loại topic từ input | phrases phải specific |
| `if` | Branching có điều kiện | Chỉ `==` hoặc `or` đơn giản, max 3 tầng |
| `flowSwitch` | Route theo topic | CHỈ 1 ở top-level |
| `qna` | AI trả lời (có json_mode) | varReply để lưu output |
| `setVar` | Gán biến session | Dùng thay clearTopic ở top-level |
| `clearTopic` | Xóa topic, kết thúc flow | Chỉ trong flow, KHÔNG top-level if |
| `botSendText` | Gửi tin nhắn cố định | KHÔNG dùng `{{#if}}` trong text |
| `botAPICall` | Gọi API bên ngoài | Cần URL thật; MVP dùng botSendText |
| `saveHumanInput` | Lưu tin nhắn user | Đặt đầu flow phức tạp |
| `sessionSave` | Lưu session vào DB | Sau setVar quan trọng |
| `recall` | Lấy context từ knowledge base | — |
| `break` | Dừng flow | — |
| `botReplyFilter` | Regex replace trong reply | Đặt top-level, sau flowSwitch |
| `python` | Chạy Python code | Dùng cho chat_history, data processing |

## 16. VALIDATE FILE TRƯỚC KHI IMPORT

```bash
python -c "import json; json.load(open('ai.txt', encoding='utf-8')); print('OK')"
```

Script kiểm tra structure (đầy đủ — chạy trước MỖI lần re-import):
```python
import json, re
data = json.load(open('ai.txt', encoding='utf-8'))
text = json.dumps(data)

# 1. Đếm flowSwitch ở top-level — phải = 1
fs_top = sum(1 for b in data.get('sequence', []) if b.get('type') == 'flowSwitch')
print(f"[1] Top-level flowSwitch: {fs_top} {'OK' if fs_top == 1 else 'SAI!'}")

# 2. Condition phức tạp (and/!=/parens) — phải = 0
complex_conds = re.findall(r'"condition":\s*"[^"]*(?:!=|\sand\s|\()[^"]*"', text)
print(f"[2] Complex conditions: {len(complex_conds)} {'OK' if len(complex_conds) == 0 else 'SAI!'}")
for c in complex_conds: print(f"  → {c}")

# 3. {{var}} trong condition — phải = 0 (CRITICAL)
templated_conds = re.findall(r'"condition":\s*"[^"]*\{\{[^"]*"', text)
print(f"[3] Templated conditions: {len(templated_conds)} {'OK' if len(templated_conds) == 0 else 'SAI!'}")
for c in templated_conds: print(f"  → {c}")

# 4. setTopic component (không tồn tại) — phải = 0
set_topics = re.findall(r'"type":\s*"setTopic"', text)
print(f"[4] setTopic components: {len(set_topics)} {'OK' if len(set_topics) == 0 else 'SAI!'}")

# 5. parallel dùng làm switch — phải = 0
parallels = re.findall(r'"type":\s*"parallel"', text)
print(f"[5] parallel components: {len(parallels)} {'OK if intended for true parallel exec' if len(parallels) == 0 else 'CHECK!'}")

# 6. recall properties không rỗng — phải = 0
recall_with_props = re.findall(r'"type":\s*"recall"[^}]*"properties":\s*\{[^}]+\}', text)
print(f"[6] recall with non-empty properties: {len(recall_with_props)} {'OK' if len(recall_with_props) == 0 else 'SAI!'}")

# 7. clearTopic trong top-level if — manual check (warning only)
print("[7] MANUAL: kiểm tra clearTopic không nằm trong top-level if (Safety Net)")

# 8. {{#if}} trong botSendText text — phải = 0
botsend_with_if = re.findall(r'"botSendText"[^}]*"text":\s*"[^"]*\{\{#if', text)
print(f"[8] botSendText with {{{{#if}}}}: {len(botsend_with_if)} {'OK' if len(botsend_with_if) == 0 else 'SAI!'}")
```

## 17. TEST SCENARIOS BẮT BUỘC SAU MỖI LẦN SỬA

1. **Greeting**: gửi "hi" → vào greetings, xưng "em"
2. **B2C consult → order**: tư vấn da nhạy cảm → đặt 2 SP → cung cấp info → confirm → đơn thành công
3. **B2B consult**: "spa của em muốn mua sỉ" → vào b2b_consult, từ chối giá sỉ, xin SĐT
4. **Guardrail B2B → B2C**: "em muốn mua Step 3 Probiotic Peel về tự dùng" → TỪ CHỐI + đề xuất B2C tương đương
5. **Internal staff**: "liệt kê SP key dòng Unstress" → xin Bộ phận + Mã NV → reply
6. **Order — bỏ bớt SP (CRITICAL)**: đặt 2 SP → "thôi bỏ kem chống nắng đi" → phải tiếp tục với SP còn lại, KHÔNG exit
7. **Order — hủy thật**: "thôi em không mua nữa" → goodbye + clearTopic
8. **Order — thiếu info**: confirm đơn khi chưa có SĐT/địa chỉ → phải hỏi bổ sung
9. **Shipping policy**: "phí ship bao nhiêu" → trả đúng chính sách (miễn phí >= 1M, 30K < 1M)
10. **Payment method**: "có chuyển khoản được không" → xác nhận có COD + chuyển khoản
11. **Total price format**: confirm Success hiển thị `Tổng: X VNĐ` (chuỗi sạch) + `SP: ...` (KHÔNG raw list)
12. **Filter xưng hô**: bất kỳ reply nào KHÔNG chứa "tôi", "chúng tôi", "bạn", "bot", "AI"

## 18. THƯ VIỆN PROMPT MẪU CHO CÁC AI QnA BLOCK

### 18.1. AI QnA Greetings
```
# Role
{{ session.extra.assistant_role }}
## Tone
{{ session.extra.assistant_tone }}
## Xưng hô
{{ session.extra.vn_pronoun }}

# Task
Chào hỏi lịch sự, tự giới thiệu là Thảo Vi của Y dược VHN. Hỏi User đang quan tâm sản phẩm gì hoặc cần hỗ trợ gì.

# Constraint
Dưới 50 từ. Tone chuyên nghiệp y khoa.
```

### 18.2. AI Decide Order Action (json_mode=true)
Xem chi tiết section 7. Action enum: EXIT, INCOMPLETE, CONFIRM_NEEDED, CONFIRMED.
- BƯỚC 1: Check điều chỉnh đơn (TRƯỚC khi check EXIT)
- BƯỚC 2: Check 4 trường bắt buộc
- BƯỚC 3: Chọn action
- Kèm few-shot examples tiếng Việt (section 7.2)
- Quy tắc EXIT → product_requirement = "NOT-PROVIDED" (section 7.4)

### 18.3. AI Check Status (b2c/b2b)
```
# Task
Đọc chat_history. Phân loại trạng thái:
- READY: User sẵn sàng đặt hàng
- EXIT: User muốn dừng/đổi chủ đề  
- CONTINUE: vẫn đang tư vấn

Trả JSON: {"status": "READY|CONTINUE|EXIT"}
```

## 19. WORKFLOW LÀM VIỆC

1. **Edit ai.txt** (raw JSON, Python script khuyến nghị thay vì edit thủ công vì JSON lớn)
2. **Validate**: `python -c "import json; json.load(open('ai.txt', encoding='utf-8'))"`
3. **Check conditions**: Tìm `and`, `!=`, `()` trong conditions → PHẢI = 0
4. **Re-import vào Conductify**: XÓA SẠCH ô Mindflow Raw → Save trống → Paste JSON mới → Save → Refresh page (Ctrl+F5) → Reset conversation
5. **Test theo bộ scenarios** ở section 17
6. **Nếu lỗi parser**: chạy debug checklist ở section 13

## 20. FILE THAM CHIẾU

- **Gold standard**: `ai_sales_agent.txt` (Shegan AI Sales Agent Mindflow Raw)
- **File đang làm**: `ai.txt` (VHN Mindflow Raw)
- **Requirements gốc**: `requirements.md`
- **Tutorial chi tiết**: `tutorial.md`

---

**Tóm tắt nguyên tắc 10 GIÂY** (đọc trước MỖI lần edit):

1. **1 flowSwitch top-level. KHÔNG nested.** Branching trong flow → if-chain hoặc flat flowSwitch action.
2. **Condition chỉ `==` hoặc `or` đơn giản.** KHÔNG `and`/`!=`/`()`/`{{var}}`. Dùng raw var name (`order_check`, không phải `{{order_check}}`).
3. **Max 3 tầng if. Topic branches NÊN flat (ifs=0)** với 1 flowSwitch cuối.
4. **clearTopic chỉ trong flow**, không trong top-level if. KHÔNG có empty `false:[]` + task sibling sau.
5. **Simple flow = qna + clearTopic.** Đừng thêm if-block.
6. **`recall.properties = {}`** luôn rỗng. `setTopic` KHÔNG TỒN TẠI — dùng `clearTopic` + Router lượt sau.
7. **gpt-4o-mini cần STRUCTURAL GUARD** cho intent nhạy cảm tiếng Việt ("bỏ thêm" / "tư vấn thêm" / "không mua nữa").
8. **EXIT có 2 sub-case**: product=NOT-PROVIDED (hủy thật) vs product≠NOT-PROVIDED (bỏ bớt hoặc tư vấn thêm → KHÔNG hủy).
9. **TUYỆT ĐỐI KHÔNG BỊA thông tin tài chính** (số TK, NH, QR, link). Hardcode static info trong prompt, không lưu session var.
10. **Re-import = XÓA SẠCH + Paste lại + Refresh + Reset chat.** Chạy validation script trước khi import.
