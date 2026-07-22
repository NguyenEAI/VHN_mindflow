# Báo cáo so sánh 2 Mindflow VHN: cơ chế lấy sản phẩm và nguyên nhân hallucinate

Ngày phân tích: 13/07/2026

File so sánh:
- `VHN_fixing.json`
- `logs_and_results/VHN_DauTien.txt`

## 1. Kết luận nhanh

`VHN_fixing.json` cho kết quả sản phẩm tốt hơn vì flow này có một tầng lấy dữ liệu sản phẩm riêng bằng API, sau đó khóa thông tin sản phẩm vào biến `session.extra.product_information` trước khi cho node tư vấn trả lời.

Ngược lại, `VHN_DauTien.txt` tuy các luồng chat đã gọn và đúng hơn về mặt hội thoại, nhưng phần sản phẩm chủ yếu dựa trực tiếp vào `knowledge_from_rag`. Khi RAG trả thiếu, trả lệch segment, hoặc model tự nối thông tin từ nhiều đoạn, bot dễ hallucinate tên sản phẩm, giá, link, ảnh hoặc mô tả.

Nói ngắn gọn:

- `VHN_fixing.json`: dữ liệu sản phẩm đi theo đường **Manager -> Query enum -> API Sheet -> Python dựng Product List -> AI chọn tên -> Python exact-match -> Recommend từ Product Information đã xác thực**.
- `VHN_DauTien.txt`: dữ liệu sản phẩm đi theo đường **Router -> B2C/B2B QnA -> Knowledge RAG -> AI tự đọc và trả lời**, có thêm bước lọc URL giả nhưng không có bước xác thực tên/giá/link/ảnh bằng dữ liệu gốc.

## 2. Cơ chế lấy sản phẩm trong `VHN_fixing.json`

### 2.1. Luồng tổng quát

Trong `VHN_fixing.json`, sản phẩm không được lấy trực tiếp trong node trả lời cuối cùng. Flow có block riêng tên:

`Lấy thông tin sản phẩm`

Block này chỉ chạy khi Manager quyết định:

```text
session.extra.previous_manager_decision.need_product_info == "yes"
```

Tức là chỉ khi user hỏi/nhắc tới sản phẩm hoặc cần đề xuất sản phẩm, flow mới đi lấy dữ liệu sản phẩm.

### 2.2. Các bước xử lý sản phẩm

**Bước 1: Manager quyết định cần lấy sản phẩm**

Node `GPT-4 MANAGER` trả JSON gồm các biến như:

```text
phase
need_product_info
customer_class
current_step
customer_name
customer_phone
user_context
target_product
note_for_sales
```

Manager có rule rất quan trọng:

```text
Khi Customer hỏi về bất kỳ sản phẩm/bộ sản phẩm cụ thể nào,
Assistant MUST ALWAYS điều hướng phase "recommend_product"
và đặt "need_product_info" là "yes"
để gọi API lấy dữ liệu sản phẩm.
```

Điểm hay: Manager chỉ quyết định luồng, không trực tiếp bịa thông tin sản phẩm.

**Bước 2: `GPT-4 Query Data` chuyển nhu cầu thành query có kiểm soát**

Node này không tự trả lời sản phẩm. Nó chỉ xuất JSON:

```json
{
  "vendor": "...",
  "product_type": "..."
}
```

Trong prompt, `vendor` bị giới hạn vào danh sách:

```text
christina, dermoaroma, floslek, ivatherm, pharmalife, preime, none
```

`product_type` cũng bị giới hạn vào danh sách:

```text
antisun, body, cleanser, cream, kit, mask, micellar, peel, serum,
supply, toner, exfoliate, others, inject, foam, none
```

Điểm hay: query được chuẩn hóa thành enum, giảm khả năng model nghĩ ra loại sản phẩm/vendor ngoài hệ thống.

**Bước 3: Python `json_check` kiểm tra output query**

Node Python kiểm tra:

- Có đủ key `vendor`, `product_type`.
- Giá trị vendor nằm trong danh sách cho phép.
- Giá trị product_type nằm trong danh sách cho phép.

Nếu hợp lệ thì trả `Yes`, không hợp lệ thì trả `No`.

Điểm hay: nếu AI query sai format, flow không dùng bừa output đó.

**Bước 4: Gọi API `product-vhn-search-data`**

Flow có const:

```text
api_url_search_data = https://n8n.workerbot.ai/webhook/product-vhn-search-data
```

Node `API CALL PRODUCT DATA` gửi body:

```json
{
  "bot_uuid": "{{ bot_uuid }}",
  "channel_type": "{{ channel_type }}",
  "channel_id": "{{ channel_id }}",
  "thread_id": "{{ thread_id }}",
  "user_msg_id": "{{ user_msg_id }}",
  "vendor": "none",
  "product_type": "{{ session.extra.query_data.product_type }}",
  "sheet_url": "https://docs.google.com/spreadsheets/d/1LdO_BV7DHdgs0_GAqTTkQbWkwefUQqw036Cb3PJcUJM/edit?usp=sharing"
}
```

Nếu query không hợp lệ, flow vẫn gọi API với:

```json
{
  "vendor": "none",
  "product_type": "none"
}
```

Điểm hay nhất của toàn bộ flow: dữ liệu sản phẩm đến từ Google Sheet/API, không phải từ trí nhớ của model.

### 2.3. Cách flow biến dữ liệu API thành nguồn sự thật

Sau API, flow parse:

```text
api_raw_product_data = json.loads(api_call_product_data)
```

Rồi kiểm tra:

```text
api_raw_product_data[0].status == "success"
```

Nếu thành công, flow chạy Python tạo:

```text
session.extra.product_wishlist
```

Biến này được dựng từ `api_raw_product_data[0].data`, gồm:

- Tên sản phẩm.
- Giá.
- Mô tả chung.
- Full description.
- Keywords.

Ở bước này, image/link đang được comment lại trong `product_wishlist`, tức danh sách này chủ yếu dùng cho AI chọn sản phẩm phù hợp, chưa phải bản trả lời cuối.

### 2.4. AI chọn sản phẩm nhưng Python mới là người xác thực

Node `GPT-4 Analysis` nhận:

```text
Product List (SOURCE OF TRUTH)
{{ session.extra.product_wishlist }}
```

Node này chỉ được phép trả JSON:

```json
{
  "name": ["Tên sản phẩm 1", "Tên sản phẩm 2"]
}
```

Prompt bắt buộc:

```text
Assistant MUST lấy ĐÚNG CHÍNH XÁC tên sản phẩm từ Product List.
KHÔNG ĐƯỢC PHÉP SAI tên sản phẩm.
```

Sau đó Python dựng:

```text
session.extra.product_information
```

Điểm cực kỳ quan trọng: Python không tin AI hoàn toàn. Nó duyệt lại toàn bộ `PRODUCTS` từ API, lấy `title = product.name`, rồi chỉ thêm sản phẩm vào `product_information` nếu:

```python
if title == names:
```

Tức là AI có chọn sai hoặc bịa tên thì Python exact-match không tìm thấy, sản phẩm đó không được đưa vào context cuối.

### 2.5. Node trả lời cuối chỉ đọc `product_information`

Node `GPT-4 Recommend Product` có đoạn:

```text
## Product List (SOURCE OF TRUTH)
ASSISTANT MUST ONLY recommend and pull data from the following verified list.
No guessing. No filling in missing values. No using product names outside this list.
"""
{{ session.extra.product_information }}
"""
```

`product_information` được Python dựng từ API và có thể chứa:

- Tên sản phẩm.
- Hình ảnh nếu có `link_image`.
- Giá nếu có `price`.
- Thành phần/công dụng/chỉ định/hướng dẫn sử dụng từ `full_description`.
- Keywords.
- Link sản phẩm nếu có `link_product`.

Prompt cuối cũng có hard rules:

```text
DO NOT self-generate image or link if missing.
DO NOT use placeholder.
ONLY IF THE PRICE IS MISSING then use "Giá tham khảo: Liên hệ".
ONLY PROVIDE INFORMATION IN THE CONTEXT OR PRODUCT LIST ABOVE.
```

Vì vậy, khả năng hallucinate ở flow này thấp hơn rõ rệt.

## 3. Cơ chế lấy sản phẩm trong `VHN_DauTien.txt`

### 3.1. Luồng tổng quát

`VHN_DauTien.txt` có cấu trúc Mindflow sạch hơn theo kiểu chuẩn:

```text
Session Manager
Router
Safety Net
Flows Switch
botReplyFilter
```

Các branch chính gồm:

```text
greetings
off_topic
handover
promotion
internal_staff
order
b2c_consult
b2b_consult
brand_info
company_info
```

Về mặt hội thoại, flow này hợp lý hơn, vì có Router/Flows Switch rõ ràng, chia B2C/B2B/order/company/brand khá mạch lạc.

Nhưng về phần sản phẩm, flow này không có block API search sản phẩm giống `VHN_fixing.json`.

### 3.2. B2C lấy sản phẩm trực tiếp từ Knowledge/RAG

Node `AI Chuyên trách B2C`:

```text
knowledge_aware = true
dataset_uuid = 550cb442-e727-4086-b0a9-9da2f5ec1a70
knowledge = {{ knowledge_from_rag }}
chat_history_aware = true
human_input_aware = true
model = gpt-4
temperature = 0.1
limit = 5
```

Prompt có rất nhiều guardrail tốt:

- Chỉ đề xuất sản phẩm homecare B2C `is_salon_product = False`.
- Giá phải khớp Knowledge.
- Không bịa link ảnh/link sản phẩm.
- Nếu thiếu sản phẩm cho một bước skincare thì phải nói rõ chưa có sản phẩm phù hợp.
- Mỗi bước skincare phải có sản phẩm cụ thể tương ứng.

Nhưng điểm yếu là node này vẫn để AI trực tiếp đọc `knowledge_from_rag` và tự viết câu trả lời cuối.

Nếu RAG trả về:

- Không đủ sản phẩm.
- Sản phẩm liên quan nhưng thiếu giá/link/ảnh.
- Nhiều segment của nhiều sản phẩm khác nhau.
- Tên sản phẩm gần giống nhau.

thì model có thể tự nối thông tin, suy diễn hoặc “điền nốt” trường thiếu.

### 3.3. B2B cũng lấy sản phẩm trực tiếp từ Knowledge/RAG

Node `AI Chuyên trách B2B`:

```text
knowledge_aware = true
dataset_uuid = 753ca5a0-738a-47a1-8cea-b50ea63a925c
knowledge = {{ knowledge_from_rag }}
chat_history_aware = true
human_input_aware = true
model = gpt-4
temperature = 0.1
limit = 5
```

Prompt B2B cũng có guardrail tốt:

- Chỉ giới thiệu sản phẩm `is_salon_product = True`.
- Giá phải khớp Knowledge.
- Không bịa giá sỉ/chiết khấu.
- Không bịa URL.
- Nếu Knowledge thiếu ảnh thì bỏ dòng hình ảnh.
- Tên sản phẩm phải ghi nguyên văn.

Nhưng giống B2C, nó vẫn phụ thuộc trực tiếp vào RAG và model.

### 3.4. Flow có bước lọc URL giả, nhưng chưa đủ

`VHN_DauTien.txt` có 2 Python node:

- `Verify URLs in B2C Reply`
- `Verify URLs in B2B Reply`

Cơ chế:

1. Lấy URL trong reply.
2. Lấy URL trong `knowledge_from_rag`.
3. Nếu reply có URL không nằm trong knowledge thì xóa dòng chứa URL đó.

Đây là một lớp bảo vệ tốt, nhưng chỉ bảo vệ được URL.

Nó không xác thực được:

- Tên sản phẩm có tồn tại không.
- Giá có đúng không.
- Link ảnh có đúng là ảnh của sản phẩm đó không nếu URL có trong RAG nhưng thuộc sản phẩm khác.
- Thành phần/công dụng có bị lấy nhầm từ sản phẩm khác không.
- Sản phẩm B2B/B2C có bị trộn không.

Vì vậy hallucination vẫn có thể xảy ra ở tên, giá, mô tả, ảnh, link ghép sai sản phẩm.

### 3.5. `findproduct_data` lưu lại từ câu trả lời đã sinh

Sau B2C, flow chạy node `AI Extract Product of Interest`, rồi lưu:

```text
session.extra.findproduct_data = extracted_product
```

Node này trích sản phẩm từ lịch sử chat:

```text
<Tên sản phẩm đầy đủ> | <giá VNĐ hoặc LIÊN HỆ>
```

Điểm yếu: nếu câu trả lời B2C trước đó đã hallucinate sản phẩm hoặc giá, thì `findproduct_data` sẽ lưu lại thông tin sai đó. Sau đó order flow dùng:

```text
{{ session.extra.findproduct_data }}
```

làm nguồn để lên đơn.

Tức là lỗi hallucination có thể lan từ tư vấn sang đặt hàng.

## 4. Bảng so sánh cốt lõi

| Tiêu chí | `VHN_fixing.json` | `VHN_DauTien.txt` |
|---|---|---|
| Cách lấy sản phẩm | Gọi API `product-vhn-search-data` từ Google Sheet | Dùng `knowledge_from_rag` trực tiếp |
| Có query chuẩn hóa vendor/product_type không | Có, bằng `GPT-4 Query Data` + Python validate | Không |
| Có dữ liệu sản phẩm thô từ DB/Sheet không | Có: `api_raw_product_data[0].data` | Không thấy API sản phẩm |
| Có bước lọc danh sách trước khi trả lời không | Có: `product_wishlist` -> AI chọn tên -> Python exact-match -> `product_information` | Không có exact-match theo DB |
| Có nguồn sự thật riêng cho node trả lời không | Có: `session.extra.product_information` | Chủ yếu là `knowledge_from_rag` |
| Có xác thực link/ảnh/giá bằng code không | Link/ảnh/giá được lấy từ object API khi dựng `product_information` | Chỉ có Python lọc URL không nằm trong RAG |
| Rủi ro bịa tên sản phẩm | Thấp, vì tên phải match đúng API data | Cao hơn, vì model tự viết từ RAG |
| Rủi ro bịa giá | Thấp hơn, giá lấy từ API object | Cao hơn, chỉ prompt cấm bịa, không có code validate |
| Rủi ro bịa link/ảnh | Thấp hơn, link/ảnh lấy từ fields `link_image`, `link_product` | Có giảm nhờ URL verifier, nhưng vẫn có thể ghép sai URL hoặc thiếu kiểm tra theo sản phẩm |
| Rủi ro lan lỗi sang order | Thấp hơn nếu `product_information` đúng | Cao hơn vì `findproduct_data` trích từ câu trả lời đã sinh |

## 5. Vì sao `VHN_fixing.json` ít hallucinate sản phẩm hơn

Có 5 lý do chính.

### 5.1. Không để node tư vấn tự tìm sản phẩm

Flow tách rõ:

- Manager quyết định có cần sản phẩm không.
- Query node biến nhu cầu thành query.
- API lấy dữ liệu thật.
- Analysis node chọn tên sản phẩm.
- Python dựng context cuối.
- Recommend node chỉ diễn đạt lại.

Đây là thiết kế rất đúng cho AI Sales Agent.

### 5.2. Có dữ liệu sản phẩm từ nguồn ngoài model

Dữ liệu sản phẩm trong `VHN_fixing.json` đến từ:

```text
Google Sheet -> n8n webhook -> api_raw_product_data
```

Model không tự nhớ giá, link, ảnh.

### 5.3. Có exact-match tên sản phẩm

Python chỉ đưa sản phẩm vào `product_information` nếu:

```python
title == names
```

Đây là điểm khóa hallucination rất mạnh. AI có thể đề xuất tên, nhưng code mới quyết định tên đó có tồn tại thật hay không.

### 5.4. Link và ảnh chỉ xuất hiện nếu object API có field thật

Trong `product_information`, ảnh chỉ được in nếu:

```python
if 'link_image' in product and product['link_image'] != 'N/A'
```

Link chỉ được in nếu:

```python
if 'link_product' in product and product['link_product'] != 'N/A'
```

Nên AI không có cơ hội tự tạo `image.jpg` hoặc URL giả nếu prompt bám đúng context.

### 5.5. Recommend node có Product List rất hẹp

Node cuối không đọc toàn bộ catalog. Nó chỉ đọc vài sản phẩm đã được lọc vào:

```text
session.extra.product_information
```

Context hẹp hơn, sạch hơn, đúng hơn.

## 6. Vì sao `VHN_DauTien.txt` dễ hallucinate sản phẩm

### 6.1. Dùng RAG trực tiếp cho câu trả lời cuối

RAG tốt nhưng không phải database query chính xác tuyệt đối. Semantic search có thể lấy:

- Segment gần nghĩa nhưng không đúng sản phẩm.
- Một đoạn có công dụng, một đoạn có giá của sản phẩm khác.
- Thiếu link hoặc thiếu ảnh.
- Dữ liệu bị cắt đoạn.

Nếu để model tự tổng hợp trực tiếp, rủi ro ghép sai là cao.

### 6.2. Prompt có guardrail nhưng thiếu enforcement bằng code

Prompt nói “không bịa” không đủ. Với sản phẩm, giá, link, ảnh, nên có code/DB xác thực.

`VHN_DauTien.txt` mới chỉ enforce URL bằng Python. Chưa enforce:

- Product name.
- Price.
- `is_salon_product`.
- Link ảnh đúng sản phẩm.
- Link sản phẩm đúng sản phẩm.

### 6.3. `findproduct_data` lưu từ output của AI

Nếu AI tư vấn sai giá, node extract có thể lưu sai giá đó vào session. Sau đó order flow dùng lại thông tin sai.

Nên lỗi không chỉ nằm ở câu trả lời tư vấn, mà có thể tiếp tục đi vào đặt hàng.

### 6.4. RAG limit 5 có thể vừa thiếu vừa nhiễu

B2C/B2B dùng `limit = 5`. Nếu user hỏi một routine nhiều bước, 5 đoạn RAG có thể không đủ để lấy đủ mỗi bước một sản phẩm. Nhưng nếu tăng limit quá cao, context lại nhiễu và tốn token.

Vì vậy với sản phẩm, API/filter theo field thường ổn hơn RAG thuần.

### 6.5. Node B2C bị giao quá nhiều việc cùng lúc

`AI Chuyên trách B2C` vừa:

- Khai thác nhu cầu.
- Tư vấn routine.
- Chọn sản phẩm.
- Kiểm tra B2B/B2C.
- Báo giá.
- Gửi link/ảnh.
- Nhắc shipping.

Một node làm quá nhiều việc từ RAG sẽ dễ trộn thông tin hơn so với pipeline nhiều bước như `VHN_fixing`.

## 7. Điểm mạnh của từng flow

### `VHN_fixing.json`

Điểm mạnh:

- Cơ chế lấy sản phẩm bằng API tốt.
- Có query enum.
- Có Python validate JSON.
- Có Python exact-match tên sản phẩm.
- `product_information` là context cuối đã được lọc.
- Prompt Recommend có “SOURCE OF TRUTH” rõ.

Điểm còn cần lưu ý:

- API body hiện đang để `"vendor": "none"` kể cả khi query có vendor. Nếu muốn lọc chính xác hơn theo brand, nên truyền `session.extra.query_data.vendor`.
- Python `product_wishlist` và `product_information` đặt `i = 1` trong vòng lặp nên số thứ tự có thể luôn là 1. Không ảnh hưởng độ đúng dữ liệu nhưng nên sửa.
- Nếu AI Analysis trả tên gần đúng nhưng không khớp 100%, Python sẽ bỏ qua sản phẩm, có thể làm `product_information` rỗng. Nên có fallback báo “chưa tìm thấy sản phẩm phù hợp” thay vì để node recommend tự xoay.
- `product_wishlist` đang bỏ link/ảnh để giảm nhiễu là hợp lý, nhưng cần đảm bảo `product_information` cuối có đủ link/ảnh cho sản phẩm đã match.

### `VHN_DauTien.txt`

Điểm mạnh:

- Cấu trúc Router/Flows Switch rõ hơn.
- B2C/B2B/order được tách flow tốt.
- Prompt B2C/B2B có guardrail khá đầy đủ.
- Có Python lọc URL giả trong reply.
- Có lưu `findproduct_data` để order dùng lại.
- Có structural guard tốt trong order.

Điểm yếu:

- Không có API search sản phẩm.
- Không có `product_information` được dựng từ dữ liệu gốc.
- Không có exact-match sản phẩm bằng code.
- URL verifier chỉ lọc URL, không lọc giá/tên/mô tả.
- Sản phẩm đã hallucinate có thể bị lưu vào `findproduct_data` và đi tiếp sang order.

## 8. Hướng khắc phục đề xuất cho `VHN_DauTien.txt`

Anh nên giữ cấu trúc hội thoại của `VHN_DauTien.txt`, nhưng mang cơ chế lấy sản phẩm của `VHN_fixing.json` sang.

### 8.1. Thêm block/API sản phẩm giống `VHN_fixing`

Thêm các thành phần:

```text
api_url_search_data = https://n8n.workerbot.ai/webhook/product-vhn-search-data
```

Thêm block trước `b2c_consult`/`b2b_consult` hoặc trong từng flow tư vấn:

```text
AI Query Product Data
Python validate query
API CALL PRODUCT DATA
Parse api_raw_product_data
Build session.extra.product_wishlist
AI Analyze Product Names
Build session.extra.product_information
```

### 8.2. Không để B2C/B2B trả lời sản phẩm từ RAG thô

Nên đổi vai trò:

- B2C/B2B QnA giai đoạn đầu: khai thác nhu cầu.
- Khi đã cần đề xuất sản phẩm: gọi API lấy sản phẩm.
- Node trả lời sản phẩm cuối chỉ dùng `session.extra.product_information`.

### 8.3. Thêm exact-match cho tên sản phẩm

Không lưu sản phẩm từ output AI nếu chưa match với dữ liệu gốc.

Logic nên là:

```text
AI chỉ được trả tên sản phẩm đã chọn.
Python exact-match tên đó với API data.
Chỉ sản phẩm match mới được đưa vào context cuối.
```

### 8.4. Xác thực cả giá, link, ảnh, không chỉ URL

Nên thay hoặc bổ sung `Verify URLs` thành `Verify Product Fields`:

- Nếu tên sản phẩm không nằm trong API data -> xóa hoặc yêu cầu trả lời lại.
- Nếu giá trong reply không khớp API data -> thay bằng giá API hoặc xóa giá.
- Nếu link/ảnh không đúng field của chính sản phẩm đó -> xóa.
- Nếu thiếu link/ảnh trong API -> không được sinh dòng link/ảnh.

### 8.5. Không lưu `findproduct_data` từ câu trả lời tự do

Thay vì extract từ `chat_history_b2c`, nên lưu từ `product_information` hoặc từ danh sách sản phẩm đã match.

Ví dụ:

```text
session.extra.findproduct_data = selected_products_from_api
```

Không nên:

```text
session.extra.findproduct_data = sản phẩm trích từ câu trả lời AI
```

vì nếu câu trả lời sai thì order sai theo.

### 8.6. Tách B2C và B2B data source rõ hơn

Khi gọi API nên truyền thêm:

```json
{
  "is_salon_product": false
}
```

cho B2C, và:

```json
{
  "is_salon_product": true
}
```

cho B2B.

Trong `VHN_fixing.json`, biến `is_salon_product` có tồn tại nhưng đoạn Python lọc đang bị comment:

```python
# IS_SALON = {{ session.extra.is_salon_product }}
# if product['is_salon_product'] == IS_SALON:
```

Khi port sang flow mới, nên bật lại logic này để tránh trộn sản phẩm homecare và salon.

## 9. Kiến trúc khuyến nghị cuối cùng

Flow tốt nhất nên là kết hợp:

```text
VHN_DauTien structure
+ VHN_fixing product retrieval pipeline
```

Tức là:

1. Giữ Router/Flows Switch của `VHN_DauTien`.
2. Giữ các flow `greetings`, `company_info`, `brand_info`, `promotion`, `order` nếu đang chạy ổn.
3. Với `b2c_consult` và `b2b_consult`, tách thành 2 giai đoạn:
   - Giai đoạn hỏi/hiểu nhu cầu.
   - Giai đoạn lấy sản phẩm bằng API và trả lời từ `product_information`.
4. Không cho node tư vấn tự bịa từ RAG khi trả sản phẩm.
5. Lưu sản phẩm đã tư vấn từ API data, không lưu từ output AI tự do.

## 10. Kết luận

Lý do `VHN_fixing.json` lấy sản phẩm tốt không phải vì prompt hay hơn đơn thuần, mà vì kiến trúc đúng hơn: dữ liệu sản phẩm được lấy từ nguồn có cấu trúc, lọc bằng code, exact-match bằng tên, rồi mới đưa vào prompt cuối.

Lý do `VHN_DauTien.txt` hay hallucinate là vì nó để AI trực tiếp đọc `knowledge_from_rag` và sinh thông tin sản phẩm cuối. Guardrail trong prompt giúp giảm lỗi, nhưng không thay thế được database/API validation.

Hướng đi nên làm: giữ khung hội thoại của `VHN_DauTien.txt`, nhưng chuyển toàn bộ cơ chế lấy sản phẩm của `VHN_fixing.json` sang, đặc biệt là 3 lớp bảo vệ:

```text
API sản phẩm thật
-> Python exact-match sản phẩm
-> Recommend chỉ từ product_information đã xác thực
```

Đây là cách vừa giữ được flow chat đang OK, vừa giảm mạnh hallucination về giá, tên sản phẩm, link và hình ảnh.
