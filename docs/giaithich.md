# GIẢI THÍCH CHI TIẾT MINDFLOW AI SALES AGENT — Y DƯỢC VHN

> **File mindflow:** `ai.txt` (Conductify AI Studio — Mindflow Raw JSON)
> **Đối tượng đọc:** AI Engineer / Sales Ops / QC nội dung
> **Cập nhật:** 2026-06-28

---

## 1. KIẾN TRÚC TỔNG QUAN

Mindflow là một **state machine** chạy tuần tự qua các `task`/`switch` ở cấp gốc `sequence[]`. Mỗi tin nhắn của khách sẽ chạy lại toàn bộ chuỗi này từ đầu. Cấu trúc cấp cao:

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Session Manager        → khởi tạo biến session.extra        │
│ 2. Router                 → phân tích human_input → topic       │
│ 3. Safety Net             → reset nếu recall_counter > 3        │
│ 4. Flows Switch           → rẽ nhánh theo topic                 │
│    ├─ greetings           ┐                                     │
│    ├─ off_topic           │                                     │
│    ├─ handover            │                                     │
│    ├─ promotion           │ Mỗi nhánh là 1 sub-flow QnA +       │
│    ├─ company_info        │ logic riêng. Kết thúc bằng          │
│    ├─ brand_info          │ clearTopic hoặc setTopic + recall.  │
│    ├─ internal_staff      │                                     │
│    ├─ b2c_consult         │                                     │
│    ├─ b2b_consult         │                                     │
│    └─ order               ┘                                     │
│ 5. Filters (5 filter)     → hậu xử lý lời thoại bot             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. SESSION MANAGER — biến cốt lõi

Khai báo trong `session.extra`:

| Biến | Mục đích |
|---|---|
| `assistant_role`, `assistant_skill`, `assistant_tone`, `vn_pronoun` | Persona — chèn vào mọi prompt QnA |
| `company_name`, `company_short_name`, `company_contact`, `company_product` | Branding |
| `shipping_policy`, `shipping_fee_threshold` (1,000,000), `shipping_fee_amount` (30,000) | Chính sách ship |
| `chat_history_b2c`, `chat_history_b2b`, `registration_chat_history`, `findproduct_chat_history` | Lịch sử hội thoại theo từng luồng (KHÔNG dùng chung) |
| `findproduct_data` | SP đã tư vấn (truyền sang order flow) |
| `old_order_customer_information` | Thông tin đơn cũ |
| `required_fields_for_b2c_order`, `required_fields_for_b2b_lead` | Checklist field bắt buộc |

---

## 3. ROUTER — phân loại 10 topic

Node `Router` (type: `router`) so khớp human_input với 10 nhóm `phrases` để gán `topic`:

| Topic | Trigger tiêu biểu |
|---|---|
| `greetings` | "chào", "hi", "alo", "shop ơi" |
| `off_topic` | "làm thơ", "viết code", chuỗi ký tự đặc biệt |
| `handover` | "gặp quản lý", "khiếu nại", "tra cứu đơn" |
| `promotion` | "khuyến mãi", "voucher", "giảm giá" |
| `company_info` | "địa chỉ", "hotline", "phí ship", "thanh toán" |
| `brand_info` | "Christina là gì", "Ivatherm xuất xứ" |
| `internal_staff` | "mã nhân viên", "liệt kê sản phẩm key" |
| `b2c_consult` | "da mình bị mụn", "kem dưỡng cho mình" |
| `b2b_consult` | "mua sỉ cho spa", "phác đồ", "Step 1-10" |
| `order` | "chốt đơn", "mua luôn", "đặt hàng" |

**Safety Net** (`recall_counter > 3`): nếu vòng lặp recall quá 3 lần → reset, thông báo lỗi đường truyền, break.

---

## 4. CHI TIẾT TỪNG SUB-FLOW

### 4.1 `greetings` / `off_topic` / `handover` / `promotion` / `brand_info` / `company_info`
- Mẫu giống nhau: 1 node `qna` + 1 node `clearTopic`.
- Riêng `handover` có 3 node: phân tích lý do (JSON) → trả lời xin lỗi + xin SĐT → clearTopic.
- Riêng `company_info` chứa cảnh báo cứng: **TUYỆT ĐỐI KHÔNG bịa số tài khoản ngân hàng** — nếu khách hỏi CK, hướng dẫn gọi hotline 0941905885.

### 4.2 `internal_staff` — xác thực nhân viên nội bộ
- 1 node QnA với prompt 2-case:
  - **CASE A** (chưa cung cấp Bộ phận + Mã NV): TUYỆT ĐỐI không trả lời, chỉ xin xác thực.
  - **CASE B** (đủ): mở đầu "Em đã ghi nhận...", trả lời từ Knowledge B2B.
- Format mã NV bắt buộc: chữ + số, tối thiểu 3 ký tự số (VD: `MKT001`, `VHN-MKT-042`).

### 4.3 `b2c_consult` — tư vấn khách lẻ
Trình tự task:

1. **Save human_input**
2. **AI Early Intent Re-check (B2C→B2B?)** — node QnA nhỏ, JSON, temp 0.1, không gọi knowledge. Trả `{"switch":"YES_B2B"}` nếu phát hiện khách thật ra là Spa/Clinic/đại lý. Nếu YES → clear history B2C + setTopic `b2b_consult` + recall **NGAY**, không gọi specialist B2C nữa. (Fix Flow 2 — chặn ngay từ đầu, tránh sinh reply "chỉ tư vấn homecare" thừa thãi.)
3. **Python — Fix URL & Price from Knowledge (B2C)** — **node validator** chạy sau specialist. Parse RAG knowledge → dict `{tên SP → (giá, link, ảnh) thật}`. Strip toàn bộ URL trong reply (tin AI 0%) → inject lại link/ảnh ĐÚNG nguyên văn cho mỗi SP có tên xuất hiện. Đồng thời so giá: nếu giá AI báo khác Knowledge → thay bằng giá thật. **Đây là chốt chặn cuối cùng để giá/link KHÔNG bao giờ bị hallucinate**, vì gpt-4o-mini có tật slugify URL từ tên SP. Logic dùng case-insensitive match + slice replacement theo index (tránh bug `str.replace()` thay nhầm SP đầu tiên).
4. **AI Chuyên trách B2C** (QnA, knowledge B2C `550cb442-...`) — chạy 9 bước:
   - B1 tên → B2 loại da → B3 tuổi → B4 tình trạng → B5 đặc biệt (thai/cho con bú nếu nữ) → B6 thói quen skincare → B7 đề xuất SP homecare (`is_salon_product=False`) → B8 thuyết phục → B9 hỏi chốt đơn.
   - **Guardrail**: chặn đề xuất SP B2B; chặn tự peel tại nhà; bắt buộc trích **Link sản phẩm + Link hình ảnh** từ mục `### Links` của Knowledge (theo đúng format `**Link sản phẩm:**`/`**Link hình ảnh:**`).
3. **Collect chat_history_b2c** (python) — append vào `session.extra.chat_history_b2c`.
4. **AI Extract Product of Interest** — extract SP gợi ý theo format `<Tên SP> | <giá>`.
5. **Save findproduct_data** — truyền sang flow `order`.
6. **AI Check B2C Status** (JSON) — trả `READY` / `CONTINUE` / `SWITCH_B2B` / `EXIT`:
   - `READY` → setTopic `order` → recall (chạy lại từ đầu, vào flow order).
   - `SWITCH_B2B` → clear `chat_history_b2c` + `findproduct_data` → setTopic `b2b_consult` → recall. **(Đây là fix cho Flow 2 — khách chuyển nhu cầu B2C→B2B giữa chừng.)**
   - `EXIT` → cảm ơn, clearTopic.
   - `CONTINUE` → gửi `bot_b2c_reply`, ở lại flow B2C.

### 4.4 `b2b_consult` — tư vấn khách Spa/Clinic
Trình tự task:

1. **Save human_input**
2. **AI Chuyên trách B2B** (QnA, knowledge B2B `753ca5a0-...`) — 9 bước:
   - Tên → Tên cơ sở + khu vực → dịch vụ → thiết bị → đề xuất SP B2B (`is_salon_product=True`, nhấn mạnh thương hiệu Christina/2000+ Spa) → phác đồ → từ chối báo chiết khấu → xin Tên + SĐT + Cơ sở + Địa chỉ.
3. **Collect chat_history_b2b** + Save session.
4. **AI Phân tích thu thập thông tin B2B** (JSON) — trả `YES` / `NO` / `EXIT` / `SWITCH_B2C`:
   - `YES` → gửi tin xác nhận lead, clear lịch sử, clearTopic.
   - `SWITCH_B2C` → clear `chat_history_b2b` → setTopic `b2c_consult` → recall.
   - `EXIT` → cảm ơn, clearTopic.
   - `NO` → gửi `bot_b2b_reply`, tiếp tục thu thập.
- **Lưu ý anti-EXIT trá hình**: khi khách hỏi giá sỉ/chiết khấu/làm đại lý → phải trả `NO` (đang quan tâm), không được trả `EXIT`.

### 4.5 `order` — chốt đơn B2C
Đây là flow phức tạp nhất. Trình tự:

1. **Save human_input**.
2. **AI Decide Order Action** — node QnA cốt lõi, trả JSON gồm `action`, `customer_name/phone/address`, `product_requirement`, `shipping_fee`, `total_price`, `payment_method`, `reply_text`. Logic 4 bước:
   - **BƯỚC 0**: chặn SP B2B (Step 1-10, Probiotic Peel, Preime SKIN RENEW...) — gợi ý phiên bản B2C tương đương hoặc khuyên đến Clinic.
   - **BƯỚC 1**: phân tích "bỏ/thêm/đổi" — hiểu chính xác "bỏ thêm X" = xóa thêm X (KHÔNG phải thêm vào).
   - **BƯỚC 2**: kiểm tra 4 field bắt buộc (`name`, `phone`, `address`, `product`).
   - **BƯỚC 3**: chọn action `EXIT` / `INCOMPLETE` / `CONFIRM_NEEDED` / `CONFIRMED`.
   - **Tính shipping**: tổng SP ≥ 1,000,000 VNĐ → `Miễn phí`; ngược lại `30,000 VNĐ`. **(Đây là chỗ vừa được củng cố bằng cảnh báo "TUYỆT ĐỐI KHÔNG mặc định 30,000 VNĐ" + few-shot "Ví dụ 1c" cho đơn mới ≥1tr.)**
   - **Anti-hallucination tài chính**: cấm bịa số tài khoản ngân hàng.
3. **Set order_info** + **Collect Register Chat History** + **Save session**.
4. **If action EXIT**:
   - SP còn 0 → cảm ơn, clear tất cả lịch sử, clearTopic.
   - SP vẫn còn (tư vấn thêm) → gửi reply, clearTopic (giữ nguyên đơn).
5. **If action CONFIRMED**:
   - Thiếu SĐT (guard cuối) → hỏi lại.
   - Đủ → gửi tin thành công + save `old_order_customer_information` + clear toàn bộ lịch sử + clearTopic.
6. **Else** (INCOMPLETE / CONFIRM_NEEDED) → gửi `order_info.reply_text`.

---

## 5. POST-PROCESS — 5 BotReplyFilter

Chạy sau MỌI lời thoại bot:

| Filter | Regex | Thay bằng |
|---|---|---|
| 1 | `tôi/Tôi` | `em` |
| 2 | `chúng tôi/chúng em/chúng mình` | `bên em` |
| 3 | `trợ lý ảo/chatbot/bot/AI` | `tư vấn viên` |
| 4 | `bạn/Bạn` | `Anh/Chị` |
| 5 | `tôi không biết/không có thông tin` | `em chưa có thông tin chi tiết về phần này` |

---

## 6. ĐỐI CHIẾU YÊU CẦU (`requirements.md`)

| # | Yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|
| 1 | Persona (Vai trò + Tone + Xưng hô VN) | ✅ Đáp ứng đầy đủ | `session.extra.assistant_role/skill/tone/vn_pronoun` |
| 2 | Phân luồng B2B vs B2C ngay câu thoại đầu | ✅ | Router với keyword `b2b_consult` (Spa/Clinic/Step) vs `b2c_consult` (tự dùng tại nhà) |
| 2.1 | Luồng bảo mật nội bộ (yêu cầu Mã NV) | ✅ | Topic `internal_staff` — CASE A/B trong prompt |
| 3.a | Không đề xuất SP B2B cho khách B2C | ✅ Củng cố mạnh | BƯỚC 0 trong `or2_qna_decide` + danh sách đối chiếu B2B→B2C + 5 few-shot |
| 3.b | Bảo mật giá sỉ, không tự bịa chiết khấu | ✅ | Bước 8 B2B + quy tắc "TUYỆT ĐỐI KHÔNG bịa giá sỉ" |
| 4 | Xử lý missing data (giá/link/ảnh) | ✅ | Mẫu câu "đang có ưu đãi đặc biệt..." trong B2C/B2B prompt |
| 5.a | B2B kết thúc bằng Tên+SĐT+Cơ sở+Địa chỉ | ✅ | `ai_b2b_check` status YES → gửi xác nhận lead |
| 5.b | B2C kết thúc bằng Tên+SĐT+Địa chỉ | ✅ | `or2_qna_decide` BƯỚC 2 — 4 field bắt buộc |
| **Bổ sung** | Trích Link SP + Link ảnh từ Knowledge | ✅ Vừa fix | Knowledge VHN dùng tên field tiếng Việt `**Link sản phẩm:**`/`**Link hình ảnh:**` — đã sửa prompt B2C để trích đúng (lỗi flow 1) |
| **Bổ sung** | Chuyển luồng B2C ↔ B2B giữa hội thoại | ✅ Vừa thêm | Status `SWITCH_B2B`/`SWITCH_B2C` + setTopic + recall (fix flow 2) |
| **Bổ sung** | Chính sách ship đúng cho đơn mới ≥1tr | ✅ Vừa fix | Đổi tiêu đề "PHẢI TÍNH ĐÚNG CHO MỌI ĐƠN" + Ví dụ 1c |
| **Bổ sung** | Anti-hallucination link/ảnh/STK | ✅ | Cảnh báo trong cả 4 prompt: B2C, B2B, order, company_info |

**Còn thiếu so với requirements** (đề xuất bổ sung):
- ❌ Chưa có node lưu lead B2B vào database/CRM (hiện chỉ gửi tin xác nhận).
- ❌ Chưa có node lưu đơn B2C vào hệ thống đặt hàng (chỉ thông báo "nhân viên VHN sẽ liên hệ").
- ⚠️ "Sản phẩm thiếu giá → trả lời xin ưu đãi" — prompt đã có nhưng chưa có few-shot cụ thể, có thể bổ sung khi gặp SP giá `LIÊN HỆ`.

---

## 7. NHỮNG ĐIỂM CẦN CHÚ Ý KHI DEBUG

1. **Knowledge B2C/B2B nằm ở 2 dataset_uuid khác nhau** (`550cb442-...` vs `753ca5a0-...`). Đảm bảo SP B2B chỉ index ở dataset B2B, ngược lại — tránh chéo.
2. **`recall_counter > 3` = vòng lặp** — kiểm tra nếu có `setTopic` chuỗi sai logic.
3. **`registration_chat_history` ≠ `chat_history_b2c`** — flow order dùng riêng, được clear khi EXIT/CONFIRMED.
4. **Filter `tôi → em`** sẽ thay cả từ `tôi` trong tên SP/Knowledge — cần test edge case.
5. **Switch luồng (SWITCH_B2B/SWITCH_B2C)** dùng `recall` để chạy lại Router. Đảm bảo `max_loop` đủ lớn (đang dùng 30).
