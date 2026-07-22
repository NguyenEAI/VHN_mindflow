# Báo cáo phân tích log tối ưu token VHN

Nguồn đọc:

- Log hội thoại: `C:\Users\Administrator\Desktop\Em trước tiên đọc cho anh hình ảnh này và viết lại thành file báo cáo cho anh nhé.md`
- Flow hiện tại: `VHN_fixing.json`
- Báo cáo cũ: `bao_cao_token_vhn.md`

## 1. Kết luận ngắn

Các lần sửa trước đã xử lý được lỗi lớn nhất: `company_branch` và `product_list` trong file hiện tại đã rỗng, `session.extra.product_wishlist` không còn bị nhét vào `GPT-4 MANAGER`. Vì vậy lỗi đốt 150K-180K token sau khi API trả catalog lớn có khả năng đã được chặn.

Tuy nhiên, nền token vẫn còn cao vì kiến trúc hiện tại vẫn là:

```text
User message
-> GPT-4 MANAGER
-> block lấy sản phẩm nếu need_product_info=yes
-> Parallel chọn nhánh trả lời
-> QnA nhánh cuối
```

Một lời chào tốn khoảng 13K token không phải do loop hay catalog nữa, mà do bot vẫn cần ít nhất 2 LLM call: `GPT-4 MANAGER` và `GPT-4o Mini Greetings`. Trong file hiện tại, prompt Manager thô dài khoảng 12.608 ký tự; sau khi render constants như `treatment`, `spa`, `agency`, độ dài xấp xỉ 19.506 ký tự. Prompt Greetings thô 3.070 ký tự; sau render constants xấp xỉ 7.791 ký tự. Cộng thêm chat history, system wrapper và output, mức 10K-13K cho greeting là dễ xảy ra.

## 2. Những gì log trước đã làm đúng

### 2.1. Đúng khi nghi ngờ hardcode Company/Product

Báo cáo token ban đầu chỉ đúng với bản production trước đó: `company_branch` và `product_list` từng rất lớn. Nhưng trong `VHN_fixing.json` hiện tại:

```text
company_branch = 0 ký tự
product_list = 0 ký tự
treatment = 4.063 ký tự
product_service_list = 517 ký tự
```

Nghĩa là phần hardcode lớn nhất đã được cắt khỏi flow hiện tại.

### 2.2. Đúng khi sửa parser JSON markdown

Log ghi nhận lỗi `Recursive infinite loop detected` do model trả JSON bọc markdown code fence. Việc thêm bước strip:

```python
MANAGER = MANAGER.strip()
if MANAGER.startswith("```json"):
    MANAGER = MANAGER[7:]
elif MANAGER.startswith("```"):
    MANAGER = MANAGER[3:]
if MANAGER.endswith("```"):
    MANAGER = MANAGER[:-3]
MANAGER = MANAGER.strip()
```

là hướng đúng. Nếu không strip, Python parse fail -> `verify_manager_decision_format = No` -> Recall chạy lại nhiều lần -> đốt token.

### 2.3. Đúng khi loại `product_wishlist` khỏi Manager

Log đã phát hiện đúng lỗi nguy hiểm: API trả nhiều sản phẩm, Python format thành `session.extra.product_wishlist`, rồi biến này bị đưa lại vào Manager/Offtopic. Nếu xảy ra, mọi tin nhắn sau đó đều phải đọc lại danh sách sản phẩm khổng lồ.

Trong file hiện tại, `product_wishlist` chỉ còn ở:

- Session init.
- Node set `session.extra.product_wishlist`.
- Node `GPT-4 Analysis`, nơi nó thật sự cần dùng để chọn sản phẩm.

Đây là trạng thái tốt hơn trước.

## 3. Những vấn đề vẫn còn trong `VHN_fixing.json`

### 3.1. `GPT-4 MANAGER` vẫn quá nặng cho nhiệm vụ router

Vị trí: `VHN_fixing.json:570`

Hiện trạng:

- instruction thô khoảng 12.608 ký tự.
- model vẫn là `gpt-4o`.
- `chat_history_aware=true`.
- `human_input_aware=true`.
- prompt vẫn chứa cả quy trình agency, retail, treatment, spa/clinic/aesthetic/hospital/pharmacy questions.

Vấn đề: Manager chỉ nên phân luồng, không nên mang toàn bộ playbook tư vấn. Mỗi tin nhắn đều đi qua Manager nên đây là nơi cần tối ưu đầu tiên.

### 3.2. Greeting vẫn là LLM call riêng

Vị trí: `VHN_fixing.json:941`

Hiện trạng:

- `GPT-4o Mini Greetings` instruction thô khoảng 3.070 ký tự.
- Sau render constants khoảng 7.791 ký tự.
- `chat_history_aware=true`, `human_input_aware=true`.

Vấn đề: Greeting/chào hỏi là flow đơn giản, có thể dùng `botSendText` hoặc QnA cực ngắn. Không cần history và không cần đầy đủ role/skill/tone dài.

### 3.3. `Parallel` vẫn tồn tại

Vị trí: `VHN_fixing.json:1303`

Hiện trạng:

```text
branches = greetings, qna, handover, off_topic, gather_requirement,
recommend_product, thank_you, agency_gather_info
```

Vấn đề: Dù condition hiện tại có vẻ loại trừ nhau theo `phase`, `parallel` vẫn là pattern rủi ro trong Conductify. Nếu có bug parse hoặc phase bị set sai/khớp nhiều điều kiện, nhiều nhánh có thể cùng chạy. Theo playbook VHN, nên dùng route độc quyền (`flowSwitch`) hoặc if-chain phẳng.

### 3.4. `product_information` bị đưa vào quá nhiều node

Vị trí:

- Set tại `VHN_fixing.json:838`.
- Inject trong `GPT-4o Mini QnA` tại `VHN_fixing.json:979`.
- Inject trong `GPT-4 Gather Requirement` tại `VHN_fixing.json:1124`.
- Inject trong `GPT-4 Recommend Product` tại `VHN_fixing.json:1162`.

Vấn đề: Chỉ `recommend_product` thật sự cần danh sách sản phẩm đã chọn. Nếu user hỏi QnA hoặc bot đang gather requirement, không nên kéo `product_information` vào prompt. Sau khi khách đã hỏi sản phẩm một lần, biến này có thể làm các lượt sau phình token.

### 3.5. API product đang không dùng vendor đã extract

Vị trí API product quanh đoạn body:

```json
"vendor": "none",
"product_type": "{{ session.extra.query_data.product_type }}"
```

Vấn đề: Node `GPT-4 Query Data` extract cả `vendor` và `product_type`, nhưng API lại hardcode `vendor = none`. Như vậy API có thể trả kết quả rộng hơn cần thiết, làm `product_wishlist` và `product_information` dài hơn.

### 3.6. Nhiều node vẫn bật history không cần thiết

Các node đang bật `chat_history_aware=true` gồm Manager, Query Data, Analysis, Greetings, QnA, Gather, Recommend, Thank you, Handover.

Vấn đề: Không phải node nào cũng cần lịch sử chat:

- `Query Data` chỉ cần message mới nhất + `target_product`.
- `Analysis` chỉ cần wishlist + user_context.
- `Greetings`, `Thank you`, `Offtopic` không cần full history.
- `Manager` chỉ cần summary ngắn, không nên đọc full history nếu đã có `previous_manager_decision`.

### 3.7. `recall` vẫn có `max_loop`

Hiện trạng:

```json
{"type": "recall", "properties": {"max_loop": "3"}}
```

Vấn đề: Theo playbook VHN/Shegan, `recall.properties` nên để `{}`. `max_loop` không phải pattern an toàn trong raw JSON và có thể gây compile/template issue.

### 3.8. Condition `attachments != []`

Vị trí: top-level `If attachments`.

Vấn đề: Playbook khuyến nghị tránh `!=` trong condition vì Conductify parser dễ lỗi. Đây chưa chắc gây token cao, nhưng nên xử lý khi refactor.

## 4. Hướng khắc phục theo thứ tự an toàn

### Giai đoạn 1: Chặn token phình lại do sản phẩm

Mục tiêu: đảm bảo lỗi 183K không quay lại.

1. Chỉ giữ `session.extra.product_information` trong `recommend_product`.
2. Gỡ `{{ session.extra.product_information }}` khỏi `qna` và `gather_requirement`.
3. Sau khi trả lời sản phẩm xong hoặc khi phase không còn là `recommend_product`, clear:

```text
session.extra.product_wishlist = ""
session.extra.product_information = ""
```

4. Giới hạn API product trả về top 5-8 sản phẩm. Nếu API chưa hỗ trợ limit, thêm bước Python cắt list trước khi format.
5. Sửa API body dùng vendor thật:

```json
"vendor": "{{ session.extra.query_data.vendor }}",
"product_type": "{{ session.extra.query_data.product_type }}"
```

Nếu vendor là array, API cần hỗ trợ array; nếu không hỗ trợ, Python phải normalize thành string hoặc `"none"`.

### Giai đoạn 2: Giảm greeting từ 13K xuống khoảng 3K-5K

1. Rút `GPT-4 MANAGER` xuống router prompt ngắn:

```text
Nhiệm vụ: phân loại phase cho tin nhắn mới nhất.
Chỉ trả JSON gồm: phase, need_product_info, customer_class, target_product, user_context, note_for_sales.
Không tư vấn, không trả lời khách.
```

2. Gỡ `{{ treatment }}` khỏi Manager. Manager chỉ cần biết "hỏi phác đồ/liệu trình -> qna", không cần toàn bộ nội dung phác đồ.
3. Gỡ câu hỏi chi tiết cho spa/phòng khám/thẩm mỹ viện/bệnh viện/nhà thuốc khỏi Manager; chuyển sang nhánh `agency_gather_info`.
4. Greeting nên đổi thành `botSendText` cố định hoặc prompt dưới 500 ký tự. Ví dụ:

```text
Dạ em chào Anh/Chị, em là Thảo Vi từ Y Dược VHN. Anh/Chị đang quan tâm sản phẩm nào hoặc cần em hỗ trợ vấn đề gì ạ?
```

5. Tắt `chat_history_aware` ở Greetings.

### Giai đoạn 3: Giảm số call và rủi ro fan-out

1. Thay `Parallel` bằng route độc quyền:
   - Lý tưởng: `flowSwitch` theo `session.extra.previous_manager_decision.phase`.
   - Nếu platform không ổn với nested flowSwitch: dùng if-chain phẳng theo phase.
2. Đảm bảo mỗi tin nhắn chỉ chạy 1 nhánh trả lời cuối.
3. Với các flow đơn giản (`greetings`, `thank_you`, `off_topic`) ưu tiên `botSendText` hoặc QnA rất ngắn.

### Giai đoạn 4: Tắt history/knowledge theo từng node

Khuyến nghị:

| Node | chat_history_aware | knowledge_aware | Ghi chú |
|---|---:|---:|---|
| Manager | Có thể tắt hoặc chỉ dùng summary | false | Dùng `previous_manager_decision` thay history dài. |
| Query Data | false | false | Chỉ cần user input + target_product. |
| Analysis | false | false | Chỉ cần product_wishlist + user_context. |
| Greetings | false | false | Có thể dùng botSendText. |
| Thank you | false | false | Có thể dùng botSendText. |
| Handover | false hoặc thấp | false | Chỉ cần issue ngắn. |
| QnA | true khi cần | true | Limit 2-3. |
| Recommend Product | true khi cần | có thể false nếu đã có API data | Chỉ inject selected products. |

### Giai đoạn 5: Sửa parser-risk

1. Đổi `recall.properties` từ `{"max_loop": "3"}` thành `{}`.
2. Thay condition `attachments != []` bằng pattern an toàn hơn theo khả năng của Conductify, hoặc đẩy check attachment vào Python/json flag rồi if `has_attachment == "yes"`.
3. Validate trước import:

```bash
python -c "import json; json.load(open('VHN_fixing.json', encoding='utf-8')); print('OK')"
```

4. Re-import sạch: xóa raw -> save trống -> paste -> save -> Ctrl+F5 -> reset conversation.

## 5. Cách test sau khi sửa

### Test token

1. Chào hỏi: "Có ai không em?"
   - Kỳ vọng sau Giai đoạn 2: khoảng 3K-5K token, không còn 13K.
2. Hỏi công ty: "Bên em phân phối thương hiệu nào?"
   - Không được gọi product API nếu chỉ hỏi danh mục brand tổng quan.
3. Hỏi sản phẩm cụ thể: "Kem trị mụn Christina nào phù hợp?"
   - Có gọi Query Data + API + Analysis + Recommend.
   - API phải filter vendor/product_type.
4. Sau khi hỏi sản phẩm xong, hỏi câu không liên quan sản phẩm.
   - Manager/QnA không được kéo lại `product_information`.

### Test chức năng

1. Chào hỏi vẫn tự nhiên, đúng xưng hô.
2. Hỏi sản phẩm vẫn không bịa giá, ảnh, link.
3. Hỏi thêm sản phẩm khác vẫn gọi API lại, không dùng nhầm sản phẩm cũ.
4. Hỏi phác đồ/liệu trình vẫn trả được từ Knowledge/QnA, không cần Manager đọc `treatment`.
5. Handover vẫn gửi thông tin khách nếu thiếu dữ liệu/khó xử lý.

## 6. Chốt hướng đi

Không nên tiếp tục tối ưu bằng cách cắt lung tung trong prompt cuối. Cần tối ưu theo nguyên tắc:

```text
Manager càng nhỏ càng tốt.
Dữ liệu lớn chỉ vào node thật sự cần.
Sản phẩm lấy bằng API/KB, giới hạn kết quả trước khi đưa vào LLM.
Flow route độc quyền, không parallel fan-out.
Session.extra không lưu text lớn lâu dài.
```

Nếu làm đúng thứ tự trên, bot vẫn giữ chức năng tư vấn sản phẩm, QnA, handover, agency/retail, nhưng token greeting có thể giảm mạnh và lỗi 183K sẽ không quay lại.
