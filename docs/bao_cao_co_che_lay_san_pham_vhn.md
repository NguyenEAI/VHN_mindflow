# PHÂN TÍCH CHUYÊN SÂU CƠ CHẾ LẤY THÔNG TIN SẢN PHẨM CỦA VHN (TỪ VHN_FIXING.JSON)

Báo cáo này phân tích chi tiết quy trình (workflow) tra cứu và lấy dữ liệu sản phẩm từ Google Sheet trong thiết kế gốc của file `VHN_fixing.json`. Đây là một luồng (flow) vô cùng thông minh, được thiết kế tinh gọn nhằm **tối ưu token cho AI** mà vẫn đảm bảo **tính chính xác (không bịa đặt - hallucination)**.

---

## TỔNG QUAN LUỒNG THỰC THI (THE SHEET PRODUCT BLOCK)

Luồng lấy sản phẩm được gói gọn trong một block tên là `Sheet Product`. Quá trình này chia làm 3 giai đoạn chính:
1. **Tiền xử lý & Trích xuất Parameter (Pre-processing)**
2. **Gọi API & Rút gọn Dữ liệu (Fetch & Token-saving Abstraction)**
3. **AI Chọn Lọc & Render Dữ liệu Chi Tiết (LLM Reasoning & Post-processing)**

Dưới đây là phân tích chi tiết từng Node trong luồng.

---

## GIAI ĐOẠN 1: TIỀN XỬ LÝ (PRE-PROCESSING)

### 1. Node QnA: `GPT-4 Query Data`
- **Chức năng:** Phân tích câu hỏi của khách hàng để bóc tách ra 2 tham số quan trọng nhất: `vendor` (Thương hiệu) và `product_type` (Loại sản phẩm).
- **Lý do thiết kế:** Thay vì dùng toàn bộ câu hỏi của khách để query (rất dễ sai sót), bot dùng LLM để phân loại câu hỏi vào các category đã được định sẵn.
- **Output:** Một chuỗi JSON chứa `vendor` và `product_type`. Ví dụ: `{"vendor": ["christina"], "product_type": ["cream"]}`.

### 2. Node Python: `Python json_check`
- **Chức năng:** Validation (Kiểm tra tính hợp lệ của JSON).
- **Cơ chế hoạt động:** 
  - Code Python sẽ parse chuỗi JSON từ LLM.
  - Kiểm tra xem 2 biến `vendor` và `product_type` có nằm trong danh sách được hardcode sẵn hay không (Ví dụ: VENDOR = ["christina", "dermoaroma"...]).
  - Trả về `"Yes"` nếu hợp lệ, `"No"` nếu JSON hỏng hoặc không thuộc danh sách.
- **Lý do thiết kế:** Đề phòng trường hợp LLM trả về dữ liệu rác, gây lỗi khi gọi API.

### 3. Node Switch (If): `If json_check == "Yes"`
- **Chức năng:** Quyết định payload để gọi API.
- **Cơ chế:** 
  - Nếu `"Yes"`: Truyền cả `vendor` và `product_type` mà LLM lấy được vào API.
  - Nếu `"No"`: Vẫn truyền `vendor` nhưng ép `product_type` về giá trị `"none"` (Cơ chế Fallback: Nếu không chắc chắn loại sản phẩm, cứ lấy toàn bộ sản phẩm của thương hiệu đó rồi để LLM tự chọn sau).

---

## GIAI ĐOẠN 2: GỌI API & RÚT GỌN (FETCH & ABSTRACTION)

### 4. Node API Call: `API CALL PRODUCT DATA`
- **Chức năng:** Kích hoạt Webhook Make.com để Make.com vào Google Sheet filter dữ liệu dựa trên `vendor` và `product_type`.
- **Dữ liệu trả về:** Một mảng JSON khổng lồ chứa chi tiết của toàn bộ các sản phẩm thỏa mãn điều kiện (gồm Tên, Giá, Ảnh, Thành phần, Công dụng...). Dữ liệu thô này được lưu vào `api_raw_product_data`.

> [!IMPORTANT] 
> **5. Node Switch (If): `Have results?` (NÚT THẮT QUAN TRỌNG NHẤT BỊ THIẾU Ở FILE LỖI)**
> - **Cơ chế:** Kiểm tra `api_raw_product_data[0].status == "success"`.
> - **Lý do thiết kế:** Nếu API lỗi (Webhook chết, Sheet bị khóa, v.v.), API sẽ không trả về success. Node này sẽ bẻ lái luồng sang nhánh `False` (Gọi API báo cáo lỗi cho Support và Recall). Nhờ vậy, chuỗi đằng sau không bao giờ bị chạy với dữ liệu rỗng. Đây chính là "công tắc chống hallucination" tuyệt đối của VHN.

### 6. Node Python: `Format Wishlist`
- **Chức năng:** Cực kỳ thông minh để tối ưu Token (Tiết kiệm chi phí API OpenAI).
- **Cơ chế:** Vì mảng dữ liệu từ API rất lớn (có thể lên tới hàng chục nghìn ký tự nếu có 10 sản phẩm), nếu nhét thẳng vào LLM sẽ cực kỳ tốn token và LLM dễ bị ngợp. Node Python này chỉ lặp qua mảng API, **bóp bỏ hoàn toàn mọi thứ (giá, ảnh, công dụng), chỉ giữ lại duy nhất TÊN SẢN PHẨM**.
- **Output:** Một danh sách Text rút gọn: 
  `- Christina Unstress Cream`
  `- Christina Line Repair Serum`
  (Lưu vào biến `session.extra.product_wishlist`).

---

## GIAI ĐOẠN 3: AI CHỌN LỌC & RENDER DỮ LIỆU CHUẨN

### 7. Node QnA: `GPT-4 Analysis`
- **Chức năng:** Chọn sản phẩm đúng nhất cho khách.
- **Cơ chế:** Truyền `product_wishlist` (Danh sách rút gọn) và `manager_decision` (Yêu cầu của Manager) vào. AI phân tích xem tên sản phẩm nào phù hợp nhất với tình trạng da của khách.
- **Output:** Mảng tên sản phẩm chính xác tuyệt đối (VD: `{"name": ["Christina Unstress Cream"]}`). Lưu vào biến `product_analyze`.

### 8. Node Python: `Format Product Info`
- **Chức năng:** Lấy lại dữ liệu chi tiết của sản phẩm mà AI vừa chọn.
- **Cơ chế (Hydration):** 
  - Node này cầm mảng Tên Sản Phẩm do `GPT-4 Analysis` chọn, dò ngược lại vào mảng gốc khổng lồ `api_raw_product_data`.
  - Hễ thấy Tên trùng khớp, nó mới lấy Giá, Ảnh, Thành phần, Công dụng của sản phẩm đó ra.
  - Xếp tất cả lại thành Format Markdown đẹp mắt và gán vào biến `session.extra.product_information`.
> [!NOTE]
> *Lưu ý về thuật toán Match:* Trong file `VHN_fixing.json` gốc, logic match là `if title == names:`. Tuy nhiên, thực tế chứng minh LLM đôi khi trả về tên bị thiếu một vài ký tự so với API, dẫn đến việc match bị thất bại. Trong luồng chuẩn hóa, em đã đổi thành Robust Matching (tìm chuỗi con `in`) để khắc phục triệt để lỗi này.

### 9. AI Trả Lời: `AI Chuyên trách B2C`
- Cuối cùng, LLM chỉ cần nhìn vào biến `session.extra.product_information` (lúc này đã chứa 1 hoặc 2 sản phẩm cực chuẩn với đầy đủ giá, hình ảnh, mô tả lấy từ Sheet) và viết câu trả lời giao tiếp với khách hàng.

---

## TỔNG KẾT BÀI HỌC ÁP DỤNG CHO CÁC MINDFLOW KHÁC

Kiến trúc tra cứu này (hay còn gọi là mô hình **LLM-Router -> Retrieve -> Abstract -> LLM-Rank -> Hydrate**) là một best-practice tuyệt vời cho việc làm RAG/Database Fetching trên Conductify:

1. **Không bao giờ nhét toàn bộ Database/API Response thẳng vào LLM**: Luôn dùng một node Python (`Format Wishlist`) để trích xuất ra một danh sách "siêu nhẹ" (chỉ gồm Tên hoặc ID) trước.
2. **LLM chỉ làm nhiệm vụ Routing và Ranking**: LLM chỉ ra quyết định xem nên chọn Tên/ID nào, chứ không bắt LLM tự sinh ra thông tin sản phẩm.
3. **Phải luôn có "Bảo Hiểm Lỗi" (`Have results?`)**: Tuyệt đối không để chuỗi Python/LLM chạy nếu API fetch thất bại, nếu không LLM sẽ rơi vào trạng thái thiếu dữ liệu và bắt đầu bịa đặt (hallucination). Khi thiết kế flow, bất cứ lệnh Call API nào cũng phải đi kèm ngay một khối rẽ nhánh IF để check status.
4. **Hydrate ở bước cuối**: Dùng Python script để lấy thông tin chi tiết gán vào biến cuối cùng, vừa format đẹp, vừa rẻ tiền (vì dùng Script miễn phí thay vì bắt LLM format).
