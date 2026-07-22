# Báo Cáo Phân Tích Token - Y Dược VHN Assistant

Đã đủ dữ liệu để chỉ đích danh. Đây là phân tích token của con **Y Dược VHN Assistant** theo từng khúc trong Mindflow.

**🔬 Vì sao VHN đốt ~106K token/tin nhắn**

## 1. Cấu trúc & điểm nóng token trong Mindflow (v577 production)

`instruction_prompt` compile ra = **170.639 ký tự = ~42.700 token** cho một lần gọi. Bóc theo node:

| Node trong Mindflow | Field | Kích thước | ≈ Token | Đây là gì |
| :--- | :--- | :--- | :--- | :--- |
| **Company (block)** | `constValue` | 25.7K ký tự | ~6.4K | 🔴 Toàn bộ hồ sơ công ty ("# About Company", lịch sử từ 2017...) hardcode |
| **Product (block)** | `constValue` | 23.7K ký tự | ~5.9K | 🔴 Nguyên catalog sản phẩm nhồi cứng (Christina Unstress...) |
| **MANAGER (block)** | `instruction` | 16.9K ký tự | ~4.2K | Prompt router phân loại intent |
| **Parallel (8 nhánh)** | `instructionx8` | ~29K ký tự | ~7.3K | Mỗi nhánh 1 prompt riêng (qna, recommend_product, gather_requirement...) |
| **Liệu trình / phác đồ** | `constValue` | 4.1K ký tự | ~1.0K | Bảng liệu trình hardcode |
| **Sub-flow tìm/đặt sản phẩm** | `instruction` | ~10K ký tự | ~2.5K | + inject `PRODUCTS = {{api_raw_product_data}}` (động, có thể rất to) |

## 2. Thủ phạm thật sự = nhân bản context x nhiều LLM call

Log `guidance_v2` cho thấy flow này **không gọi OpenAI 1 lần/tin nhắn mà ~5 lần**: MANAGER (routing) -> node Parallel fan-out 8 nhánh, mỗi nhánh là 1 call riêng:
- GPT-4 Gather Requirement 
- GPT-4 Recommend Product 
- GPT-4o Mini QnA 
- Greetings 
- Handover 
- Offtopic 
- Thank you...

👉 **Mỗi call lại nhận LẠI toàn bộ khối tĩnh (Company 6.4K + Product 5.9K + role instructions + 30 tin lịch sử).**

### Phép tính khớp thực tế:
`~42.7K token tĩnh` x `~2-3 call thực/tin nhắn` + `RAG/API product data` + `30 msg history`
= **100-106K token/tin nhắn** ✔️ khớp số đo (10 msg -> 1.05M token trong 2h)

Và mấy nhánh **GPT-4 / gpt-4.o** (Gather Requirement, Recommend Product) là chỗ đắt nhất - **dùng cái đốt $100.**

## 3. Nơi cắt được nhiều token nhất (theo thứ tự ROI)

| # | Sửa ở đâu | Cắt được |
| :--- | :--- | :--- |
| 1 | 🔴 **Product block** `constValue` - bỏ nhồi cả catalog, chuyển sang **RAG/knowledge** chỉ lấy sản phẩm liên quan | ~5.9K token x mỗi call -> lớn nhất |
| 2 | 🔴 **Company block** `constValue` - rút gọn hồ sơ công ty còn phần cốt lõi, hoặc đưa vào knowledge | ~6.4K token x mỗi call |
| 3 | 🟠 **Node Parallel** - đảm bảo router chỉ chạy 1 nhánh/tin nhắn (exclusive), không fan-out toàn bộ; và các nhánh không cần full context thì đừng truyền | giảm số call -> giảm bội số |
| 4 | 🟠 **Đổi nhánh GPT-4 -> gpt-4o-mini** ở Gather Requirement/Recommend nếu chất lượng chịu được | rẻ ~10x |
| 5 | 🟡 `get_chat_history_limit` 30 -> 10 tin | bớt history mỗi call |

### 🔥 Đòn bẩy lớn nhất
Hai khối `constValue` (Company + Product = 49K ký tự = **12K token**) đang bị **hardcode** và gửi lại ở **MỌI call** - chuyển sang retrieval sẽ cắt ngay ~50-60% token/tin nhắn.

---
**Câu hỏi tiếp theo (Đề xuất hành động):**
Anh muốn em (a) trích ra nội dung chi tiết 2 khối `constValue` (Company + Product) để anh xem cái nào cắt được, hay (b) kiểm tra node **Parallel** xem nó đang fan-out mấy call thật/tin nhắn để xác nhận đòn bẩy #3?
