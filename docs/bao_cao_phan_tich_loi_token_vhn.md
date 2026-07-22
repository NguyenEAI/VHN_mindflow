# Báo cáo 1: Phân tích vấn đề token và rủi ro trong `VHN_fixing.json`

## Kết luận nhanh

Vấn đề không nằm ở một prompt đơn lẻ mà nằm ở kiến trúc gọi nhiều LLM call cho cùng một tin nhắn. File `VHN_fixing.json` đang có 12 node QnA, tổng riêng `instruction` khoảng 53.187 ký tự, cộng thêm constants, chat history, knowledge results và dữ liệu sản phẩm động. Mỗi tin nhắn thường đi qua `MANAGER`, có thể đi qua block lấy sản phẩm, rồi mới qua nhánh trả lời trong `Parallel`.

Theo `bao_cao_token_vhn.md`, bản production v577 từng đốt khoảng 100K-106K token/tin nhắn vì vừa nhồi Company/Product lớn, vừa nhân bản context qua nhiều call. Trong file `VHN_fixing.json` hiện tại, phần `product_list` đã rỗng và Company không còn khối 25K ký tự như báo cáo cũ, nhưng các điểm nóng chính vẫn còn: prompt `MANAGER` dài, `Parallel` nhiều nhánh, nhiều node bật `chat_history_aware`, và dữ liệu sản phẩm được lưu vào `session.extra` rồi inject lại vào các node sau.

## Điểm nóng cụ thể trong file

| Vị trí | Node | Kích thước / cấu hình | Vấn đề |
|---|---:|---:|---|
| `VHN_fixing.json:570` | `GPT-4 MANAGER` | instruction ~12.608 ký tự, model `gpt-4o`, history=true, human=true | Luôn chạy để route phase. Prompt quá dài cho nhiệm vụ phân loại. |
| `VHN_fixing.json:887` | `Lấy thông tin sản phẩm` | chạy khi `need_product_info == "yes"` | Nếu user hỏi sản phẩm, flow phát sinh thêm nhiều bước: Query Data -> API -> Analysis -> lưu sản phẩm. |
| `VHN_fixing.json:695` | `GPT-4 Query Data` | instruction ~5.620 ký tự | Chỉ cần extract `vendor/product_type` nhưng prompt đang dài. |
| `VHN_fixing.json:821` | `GPT-4 Analysis` | instruction ~2.031 ký tự | Lọc lại sản phẩm từ danh sách API trả về, nhưng vẫn bật history/human. |
| `VHN_fixing.json:1162` | `GPT-4 Recommend Product` | instruction ~7.218 ký tự, model `gpt-4o`, knowledge=true, history=true, max_tokens=2000 | Vừa đắt vừa nhận `session.extra.product_information`, dễ phình token nếu API trả nhiều sản phẩm. |
| `VHN_fixing.json:1303` | `Parallel` | 8 nhánh: greetings, qna, handover, off_topic, gather_requirement, recommend_product, thank_you, agency_gather_info | Nếu engine compile/fan-out không chặt, context bị nhân theo nhánh. |

## Nguyên nhân gốc

1. `MANAGER` làm quá nhiều việc trong một prompt: phân loại phase, phân loại customer, tóm tắt context, quyết định có cần sản phẩm, hướng dẫn sales, kèm nhiều rule nghiệp vụ dài. Với nhiệm vụ router, node này nên trả JSON rất ngắn.

2. `Parallel` là bộ nhân chi phí. Dù conditions có vẻ loại trừ nhau, cấu trúc `parallel` trong Conductify có rủi ro fan-out hoặc compile nhiều nhánh. Playbook VHN khuyến nghị dùng `flowSwitch`/route phẳng thay vì dùng `parallel` như switch.

3. Hầu hết QnA đều bật `chat_history_aware=true` và `human_input_aware=true`. Các node như greetings, thank_you, handover, Query Data, Analysis không cần toàn bộ history. Khi history dài, token tăng theo từng call.

4. Dữ liệu sản phẩm động được đưa vào `session.extra.product_wishlist` và `session.extra.product_information`. Sau đó `product_information` lại được inject vào `qna`, `gather_requirement`, `recommend_product`. Nếu API trả nhiều sản phẩm hoặc mô tả dài, mỗi node sau đó đều kéo theo một khối sản phẩm lớn.

5. `knowledge_aware=true` ở `qna` và `recommend_product` với limit 5. Khi cộng thêm chat history và product_information, mỗi lượt trả lời sản phẩm có thể nhận đồng thời: prompt dài + RAG results + history + dữ liệu API sản phẩm.

6. Một số pattern cấu trúc còn rủi ro parser: `recall` có `max_loop`, condition `attachments != []`, và không có top-level `flowSwitch`. Đây không phải thủ phạm token chính, nhưng nên sửa khi refactor để tránh lỗi production khó đoán.

## Cách khắc phục theo ROI

1. Rút `GPT-4 MANAGER` xuống thành router JSON tối giản, mục tiêu dưới 2.000-3.000 ký tự. Output chỉ cần: `phase`, `need_product_info`, `customer_class`, `target_product`, `user_context`, `note_for_sales`. Chuyển các ví dụ dài và rule tư vấn sang node chuyên trách.

2. Đổi `MANAGER`, `Gather Requirement`, `Recommend Product` từ `gpt-4o` sang `gpt-4o-mini` nếu test chất lượng đạt. Với router/extract JSON, nên dùng model rẻ và temperature thấp.

3. Thay `Parallel` bằng route độc quyền: `router/flowSwitch` hoặc if-chain phẳng. Mỗi lượt chỉ được chạy đúng một nhánh trả lời.

4. Giảm context từng node:
   - `MANAGER`: không cần knowledge, chỉ cần human input + summary ngắn.
   - `Query Data`: không cần full chat history, chỉ cần `target_product` và message mới nhất.
   - `Analysis`: không cần chat history, chỉ cần `product_wishlist` + `user_context`.
   - `Greetings`, `Thank you`, `Offtopic`: tắt history nếu không bắt buộc.

5. Giới hạn dữ liệu sản phẩm từ API trước khi đưa vào prompt. API chỉ nên trả top 5-8 sản phẩm, mỗi sản phẩm chỉ gồm `id/name/price/short_description/link_image/link_product`. Full description chỉ lấy ở bước cuối khi đã chọn tên/id sản phẩm.

6. Không lưu full catalog/full product description dài vào `session.extra`. Chỉ lưu `selected_product_ids` hoặc một bản tóm tắt ngắn. Sau khi trả lời xong, clear `session.extra.product_wishlist` và `session.extra.product_information`.

7. Giảm `knowledge result limit`: bắt đầu với 2-3 cho QnA và Recommend. Chỉ tăng nếu test Quick Test cho thấy thiếu dữ liệu.

8. Giảm `max_tokens`:
   - Router/extract JSON: 300-500.
   - Query Data/Analysis: 500-800.
   - Recommend Product: 1000-1200 nếu chỉ trả 2-3 sản phẩm.

9. Sửa pattern parser:
   - `recall` properties nên để `{}` thay vì `{"max_loop":"3"}`.
   - Tránh `!=` trong condition, thay `attachments != []` bằng check khác an toàn hơn theo engine hiện tại.
   - Khi refactor lớn, đưa flow về pattern `session -> router -> safety -> flowSwitch -> filters`.

## Checklist test sau khi sửa

1. Tin nhắn chào hỏi chỉ chạy `MANAGER` + `greetings`, không gọi product API.
2. Hỏi một sản phẩm cụ thể chạy `MANAGER` + `Query Data` + API + `Analysis` + `Recommend Product`.
3. Hỏi công ty/chính sách không inject `product_information`.
4. Hỏi "còn sản phẩm nào khác không" vẫn lấy sản phẩm mới nhưng API trả giới hạn.
5. Sau 10-20 lượt chat, `session.extra.product_information` không tăng vô hạn.
6. Log token/tin nhắn giảm ít nhất theo 3 mốc: sau khi rút Manager, sau khi giới hạn API product, sau khi bỏ Parallel.
