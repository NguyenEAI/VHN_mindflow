# KẾ HOẠCH TRIỂN KHAI AI SALES AGENT – Y DƯỢC VHN

> **Dự án:** AI Agent tư vấn bán hàng cho Công ty CP XNK & Phân Phối Sản Phẩm Y Dược VHN  
> **Nền tảng:** Conductify AI Studio  
> **Ngày lập:** 2026-06-18  

---

## MỤC LỤC

1. [Tổng quan dự án](#1-tổng-quan-dự-án)
2. [Phân tích dữ liệu đầu vào](#2-phân-tích-dữ-liệu-đầu-vào)
3. [Kiến trúc AI Agent (Mindflow)](#3-kiến-trúc-ai-agent-mindflow)
4. [Kế hoạch triển khai từng giai đoạn](#4-kế-hoạch-triển-khai-từng-giai-đoạn)
5. [Hướng dẫn chi tiết từng bước trên Conductify Studio](#5-hướng-dẫn-chi-tiết-từng-bước-trên-conductify-studio)
6. [Chi tiết kỹ thuật Mindflow](#6-chi-tiết-kỹ-thuật-mindflow)
7. [Kịch bản test & tiêu chí nghiệm thu](#7-kịch-bản-test--tiêu-chí-nghiệm-thu)
8. [Triển khai đa kênh & Bàn giao](#8-triển-khai-đa-kênh--bàn-giao)
9. [Rủi ro & giải pháp](#9-rủi-ro--giải-pháp)
10. [Checklist tổng hợp](#10-checklist-tổng-hợp)

---

## 1. TỔNG QUAN DỰ ÁN

### 1.1. Thông tin doanh nghiệp
- **Tên:** Công ty CP XNK & Phân Phối Sản Phẩm Y Dược VHN
- **Lĩnh vực:** Dược mỹ phẩm quốc tế & giải pháp da liễu thẩm mỹ
- **7 nhãn hàng:** Christina, Ivatherm, Floslek, Dermoaroma, Preime, Pharmalife (+ 1 nhãn nữa theo sheet)
- **Website:** vhndistribution.com
- **VP Sài Gòn:** Tầng 5A, 407 Tô Hiến Thành, P.14, Q.10, TP.HCM
- **VP Hà Nội:** Số 14 Láng Hạ, P.Thành Công, Q.Ba Đình, Hà Nội

### 1.2. Mục tiêu AI Agent (theo yêu cầu sếp)

| Mục tiêu | Mô tả |
|-----------|--------|
| Phân luồng khách hàng | Sàng lọc B2B/B2C/Nội bộ ngay từ câu thoại đầu tiên |
| Tư vấn sản phẩm đúng đối tượng | B2B → SP chuyên nghiệp (is_salon_product=True), B2C → SP homecare (is_salon_product=False) |
| Chốt đơn B2C | Thu thập Tên + SĐT + Địa chỉ giao hàng → lên đơn bán lẻ |
| Thu lead B2B | Thu thập Tên + SĐT + Tên cơ sở (Spa/Clinic) + Địa chỉ → chuyển Sales |
| Bảo mật nội bộ | Yêu cầu Bộ phận + Mã số nhân viên khi hỏi thông tin nội bộ |
| Guardrails | Không đề xuất SP B2B cho khách B2C, không bịa giá sỉ/chiết khấu, không hallucination |
| Xử lý Missing Data | SP thiếu giá → dùng mẫu câu xin SĐT (không bịa giá) |

### 1.3. Persona AI Agent (theo đề xuất sếp – PHẦN 2 mục 1)

- **Vai trò:** Chuyên viên tư vấn da liễu và chăm sóc khách hàng đại diện cho Công ty Y dược VHN
- **Giọng điệu (Tone of voice):** Chuyên nghiệp, lịch sự, chuẩn y khoa, tận tâm và đáng tin cậy
- **Xưng hô:** "Dạ, em chào Anh/Chị", "Y dược VHN xin phép được hỗ trợ..."
- **Cách trả lời:** Ngắn gọn dưới 80 từ, xúc tích, đi thẳng vấn đề

> **Lưu ý:** Persona ban đầu trong sheet AI là "Thảo Vi" (giọng thân thiện, gần gũi). Sếp đề xuất chuyển sang persona "Chuyên viên tư vấn da liễu" (giọng chuyên nghiệp, chuẩn y khoa). **Ưu tiên dùng persona sếp yêu cầu.**

---

## 2. PHÂN TÍCH DỮ LIỆU ĐẦU VÀO

### 2.1. Tổng quan các sheet trong file Excel

| Sheet | Số dòng | Mục đích | Trạng thái |
|-------|---------|----------|------------|
| Company | 28 | Thông tin doanh nghiệp | Đã điền cơ bản (thiếu USP, chính sách) |
| Giới thiệu 7 nhãn hàng | 42 | Key giới thiệu + Key tư vấn từng nhãn | Đã điền chi tiết Christina, Ivatherm, Floslek, Pharmalife |
| AI | 20 | Persona, mục tiêu, giọng điệu | Đã điền đầy đủ |
| Kịch bản bán hàng | 97 | Quy trình tư vấn + kịch bản mẫu B2B/B2C/Nội bộ | Đã điền chi tiết |
| QnA | 237 | Câu hỏi – Câu trả lời thường gặp | Đã điền |
| Phác đồ trị liệu | 12 | Liệu trình phác đồ VHN | Có tiêu đề, dữ liệu trống |
| Phác đồ Christina | 85 | Phác đồ chi tiết từng dòng Christina | Đã điền chi tiết (BioPhyto, Unstress...) |
| Phác đồ Christina + Máy | 73 | Phối hợp Christina với máy công nghệ cao | Đã điền |
| Product | 257 | Toàn bộ sản phẩm (240+ SP) | 98 B2B, 142 B2C, 17 chưa phân loại |
| Product Christina | 187 | Riêng SP Christina | Subset của Product |
| Account | 8 | Tài khoản quản trị | Chưa tạo |

### 2.2. Phân tích dữ liệu sản phẩm (Product)

**Thống kê:**
- Tổng: 257 sản phẩm (bao gồm cả header)
- B2B (is_salon_product = True): 98 SP
- B2C (is_salon_product = False): 142 SP
- Chưa phân loại: ~17 SP

**Vendor phân bổ:**

| Vendor | Số SP |
|--------|-------|
| Christina | 187 |
| Ivatherm | 22 |
| Floslek | 16+3 (lỗi tên) |
| Dermoaroma | 12 |
| Preime | 10 |
| Pharmalife | 7 |

**Dữ liệu khuyết thiếu (QUAN TRỌNG):**

| Trường | Số SP thiếu | Ghi chú |
|--------|-------------|---------|
| price | 66 SP | ~26% SP thiếu giá → cần xử lý đặc biệt |
| link_image | 73 SP | ~28% thiếu ảnh |
| full_description | 1 SP | Gần đầy đủ |
| Công dụng / Chỉ định / HDSD | Hầu hết trống | Thông tin nằm trong full_description |

### 2.3. 14 sản phẩm thử nghiệm (theo yêu cầu sếp – PHẦN 1)

#### Nhóm B2B (7 SP) – `is_salon_product = True`

| ID | Tên sản phẩm | Giá |
|----|-------------|-----|
| 1 | Christina - Unstress - Step 1: Gentle Cleansing Milk - 300ml | 2,398,000 VNĐ |
| 2 | Christina - Unstress - Step 2: Revitalizing Toner - 300ml | 2,266,000 VNĐ |
| 3 | Christina - Unstress - Step 3: Probiotic peel - 250ml | 7,282,000 VNĐ |
| 4 | Christina - Unstress - Step 4: Frangipani Concentrate - 300ml | 2,800,000 VNĐ |
| 5 | Christina - Unstress - Step 5: Total Serenity Serum - 100ml | 7,150,000 VNĐ |
| 6 | Christina - Unstress - Step 6a: Relaxing Massage Cream - 500ml | 3,300,000 VNĐ |
| 220 | Preime - SKIN RENEW Skin Renewal Solution | 6,600,000 VNĐ |

#### Nhóm B2C (7 SP) – `is_salon_product = False`

| ID | Tên sản phẩm | Giá |
|----|-------------|-----|
| 11 | Christina - Unstress - Gentle Cleansing Milk - 300ml | 1,900,000 VNĐ |
| 12 | Christina - Unstress - Stabilizing Toner - 300ml | 1,900,000 VNĐ |
| 13 | Christina - Unstress - Total Serenity Serum - 50ml | 3,190,000 VNĐ |
| 14 | Christina - Unstress - Probiotic Day Cream SPF 15 - 50ml | 3,410,000 VNĐ |
| 15 | Christina - Unstress - Harmonizing Night Cream - 50ml | 2,860,000 VNĐ |
| 16 | Christina - Unstress - Replenishing Mask - 50ml | 2,100,000 VNĐ |
| 191 | Ivatherm - Cicaderm Cream - 40ml | 715,000 VNĐ |

> **Chiến lược cuốn chiếu (theo lời khuyên sếp):** Huấn luyện với 14 SP này trước → test luồng mượt mà → mới nạp toàn bộ 240+ SP.

### 2.4. Vấn đề dữ liệu cần xử lý trước khi nạp

1. **Tên vendor Floslek bị lỗi:** Có 3 SP tên vendor chứa ký tự thừa (`\n \t\nFloslek`, `\nFloslek`) → cần chuẩn hóa
2. **66 SP thiếu giá:** Cần cấu hình AI phản hồi theo mẫu câu sếp yêu cầu (xin SĐT để báo giá)
3. **73 SP thiếu link ảnh:** AI không gửi ảnh khi thiếu → cần thông báo khéo
4. **Cột `Công dụng`, `Chỉ định`, `Hướng dẫn sử dụng` hầu hết trống:** Thông tin đã nằm trong `full_description` → dùng full_description làm nguồn chính
5. **Cột `combo` toàn bộ = False:** Chưa có data combo → chưa thể gợi ý combo tự động
6. **Sheet Company thiếu:** USP, chính sách bán hàng, vận chuyển, đổi trả, bảo mật → **cần bổ sung từ VHN trước khi triển khai**

---

## 3. KIẾN TRÚC AI AGENT (MINDFLOW)

### 3.1. Flowchart tổng thể (theo sơ đồ sếp – PHẦN 3)

```
[BẮT ĐẦU] -> Khách hàng nhắn tin chào hỏi / hỏi sản phẩm
   |
   v
[BƯỚC 1: SÀNG LỌC ĐỐI TƯỢNG]
   |-- Khách hỏi thông tin nội bộ công ty 
   |     -> Yêu cầu nhập Mã nhân viên -> Xác thực -> Trả lời thông tin
   |
   |-- Khách hỏi mua sỉ / Spa / Clinic 
   |     -> [CHUYỂN SANG LUỒNG B2B]
   |
   |-- Khách hỏi mua lẻ / tư vấn da cá nhân 
   |     -> [CHUYỂN SANG LUỒNG B2C]
   |
   |-- Chưa rõ ràng 
         -> AI hỏi khéo léo: "Dạ, không biết Anh/Chị đang cần tìm SP 
            để chăm sóc da tại nhà hay dùng cho dịch vụ tại Spa/phòng khám ạ?"


===================== LUỒNG B2B (ĐẠI LÝ / SPA) =====================

[BƯỚC 2: KHAI THÁC THÔNG TIN CƠ SỞ]
   |-- Hỏi tên khách, tên Spa/Phòng khám, khu vực hoạt động.
   |-- Hỏi về dịch vụ chính + thiết bị công nghệ cao đang dùng.

[BƯỚC 3: ĐỀ XUẤT GIẢI PHÁP CHUYÊN NGHIỆP]
   |-- Giới thiệu SP chuyên nghiệp (B2B - is_salon_product = True).
   |-- Nhấn mạnh hiệu quả trị liệu lâm sàng và uy tín thương hiệu.

[BƯỚC 4: THU THẬP THÔNG TIN LIÊN HỆ]
   |-- AI khéo léo từ chối báo chiết khấu chi tiết qua chat.
   |-- Xin Tên + SĐT + Tên cơ sở + Địa chỉ → chuyển Sales. -> [KẾT THÚC]


===================== LUỒNG B2C (KHÁCH LẺ) =====================

[BƯỚC 2: KHAI THÁC TÌNH TRẠNG DA]
   |-- Hỏi loại da (Dầu, khô, hỗn hợp), độ tuổi, tình trạng da.
   |-- Hỏi thói quen skincare + lưu ý đặc biệt.

[BƯỚC 3: ĐỀ XUẤT ROUTINE TẠI NHÀ]
   |-- Đề xuất SP B2C (is_salon_product = False) phù hợp.
   |-- Giải thích công dụng, cách dùng, giá bán lẻ niêm yết.

[BƯỚC 4: CHỐT ĐƠN & THU THẬP THÔNG TIN GIAO HÀNG]
   |-- Xin Tên + SĐT + Địa chỉ → lên đơn giao hàng. -> [KẾT THÚC]
```

### 3.1.1. Ánh xạ Flowchart → Mindflow Topics

```
[User nhắn tin]
    │
    ▼
[Session Manager] ── Extra fields: {customer_type, customer_name, phone, address, 
    │                                 facility_name, cart, employee_id, employee_dept}
    ▼
[Router] ── Topics:
    │   ├── greetings        → Flow Chào hỏi
    │   ├── off_topic        → Flow Off-topic  
    │   ├── company_info     → Flow Thông tin chung
    │   ├── brand_info       → Flow Giới thiệu nhãn hàng
    │   ├── b2b_consult      → Flow Tư vấn B2B (Đại lý/Spa)
    │   ├── b2c_consult      → Flow Tư vấn B2C (Khách lẻ)
    │   ├── order            → Flow Đặt hàng
    │   ├── internal_staff   → Flow Nhân sự nội bộ
    │   ├── handover         → Flow Gọi hỗ trợ
    │   └── promotion        → Flow Khuyến mãi
    │
    ▼
[Flows Switch] ── Phân phối vào từng Flow
```

### 3.2. Chi tiết từng Flow

#### Flow 1: Chào hỏi (greetings)
```
[AI QnA] ── Instruction: Chào hỏi với persona Thảo Vi
    │        Knowledge: General Knowledge + QnA dataset
    │        Temperature: 0.7
    ▼
[Filter Bot Reply] ── Thay thế cách xưng hô (nếu cần)
    ▼
[Clear Topic]
```

#### Flow 2: Sàng lọc & Phân luồng (screening)
```
[AI QnA – AI Phân tích] 
    │  Instruction: Phân tích ý định: B2B / B2C / Nội bộ / Chưa rõ
    │  Enable JSON Mode: ON (chỉ GPT)
    │  Output JSON: {"customer_type": "b2b|b2c|internal|unclear"}
    │  Variable to save: ai_screening_reply
    ▼
[Set Var] ── customer_type = json.loads(ai_screening_reply).customer_type
    ▼
[Parallel] ── 4 nhánh:
    ├── customer_type == "b2b"      → [Set Topic: b2b_consult] → [Recall]
    ├── customer_type == "b2c"      → [Set Topic: b2c_consult] → [Recall]
    ├── customer_type == "internal" → [Set Topic: internal_staff] → [Recall]
    └── customer_type == "unclear"  → [Bot Send Text: "Dạ, không biết Anh/Chị 
                                        đang cần tìm SP để chăm sóc da tại nhà 
                                        hay dùng cho dịch vụ tại Spa/phòng khám ạ?"]

Lưu ý: KHÔNG đặt Clear Topic ở luồng dùng Recall (theo hướng dẫn Buổi 9 – mục 3.5.1)
```

#### Flow 3: Tư vấn B2B (b2b_consult)
```
[AI QnA Chuyên trách B2B]
    │  Instruction prompt: xem mục 6.3
    │  Enable Knowledge Aware: ON
    │  Knowledge Dataset UUID: (lấy từ Book vhn_b2b_product)
    │  Knowledge Dataset QA UUID: (lấy từ QnA Library vhn_qna)
    │  Knowledge Result Limit: 3
    │  Enable Chat History Aware: ON
    │  Enable Human Input Aware: ON
    │  Variable to save: bot_b2b_reply
    │  Temperature: 0.7
    │  Max Tokens: 500
    ▼
[Filter Bot Reply] ── Regex: (?:trợ lý ảo|chatbot|bot|AI) → Replace: tư vấn viên
    ▼
[Bot Send Text] ── {{bot_b2b_reply}}
    ▼
[Python Block] ── Lưu chat_history vào Session Extra
    │  Code: (xem mục 6.7)
    ▼
[AI QnA – AI Phân tích] 
    │  Instruction: "Phân tích cuộc hội thoại, kiểm tra khách đã cung cấp đủ 
    │   Tên + SĐT + Tên cơ sở + Địa chỉ chưa?"
    │  Enable JSON Mode: ON
    │  Output: {"status": "YES|NO|EXIT", "name":"...", "phone":"...", "facility":"...", "address":"..."}
    │  Variable to save: ai_b2b_check
    ▼
[Set Var] ── b2b_info = json.loads(ai_b2b_check)
    ▼
[Parallel] ── 3 nhánh:
    ├── b2b_info.status == "YES" 
    │     → [Bot API Call] POST https://api.workerbot.ai/v1/contact-list/create
    │       Body: xem mục 6.6 (Lead B2B)
    │     → [Bot Send Text] "Cảm ơn Anh/Chị, chuyên viên kinh doanh sẽ liên hệ 
    │        trong thời gian sớm nhất ạ!"
    │     → [Clear Topic]
    │
    ├── b2b_info.status == "NO"
    │     → (Không Clear Topic → giữ trong luồng để tiếp tục hỏi lần sau)
    │
    └── b2b_info.status == "EXIT"
          → [Bot Send Text] "Dạ, cảm ơn Anh/Chị đã quan tâm..."
          → [Clear Topic]
```

#### Flow 4: Tư vấn B2C (b2c_consult)
```
[AI QnA Chuyên trách B2C]
    │  Instruction prompt: xem mục 6.4
    │  Enable Knowledge Aware: ON
    │  Knowledge Dataset UUID: (lấy từ Book vhn_b2c_product)
    │  Knowledge Dataset QA UUID: (lấy từ QnA Library vhn_qna)
    │  Knowledge Result Limit: 3
    │  Enable Chat History Aware: ON
    │  Enable Human Input Aware: ON
    │  Variable to save: bot_b2c_reply
    │  Temperature: 0.7
    │  Max Tokens: 500
    ▼
[Filter Bot Reply] ── Regex: (?:trợ lý ảo|chatbot|bot|AI) → Replace: tư vấn viên
    ▼
[Bot Send Text] ── {{bot_b2c_reply}}
    ▼
[AI QnA – AI Phân tích]
    │  Instruction: "Khách đã sẵn sàng mua chưa?"
    │  Output: {"status": "READY|CONTINUE|EXIT"}
    │  Variable to save: ai_b2c_check
    ▼
[Parallel]
    ├── READY    → [Set Topic: order] → [Recall]
    ├── CONTINUE → (Giữ trong luồng, tiếp tục tư vấn)
    └── EXIT     → [Bot Send Text: cảm ơn] → [Clear Topic]
```

#### Flow 5: Đặt hàng (order) – Áp dụng mẫu Buổi 11
```
[A. AI QnA – AI Tổng quản] 
    │  KHÔNG bật Chat History Aware & Human Input Aware
    │  (Tránh ghi nhớ đơn hàng cũ – theo hướng dẫn Buổi 11 mục 4.2.5)
    │  Enable JSON Mode: ON
    │  Instruction: "Parse thông tin đặt hàng thành JSON"
    │  Output: {products, quantities, name, phone, address, confirm}
    │  Variable to save: ai_order_parse
    ▼
[B. Set Var] ── order_info = json.loads(ai_order_parse)
    ▼
[C. Python Block – Check biến]
    │  Kiểm tra đã đủ: products, name, phone, address
    │  print("YES") nếu đủ, print("NO") nếu chưa
    │  Variable to save: order_check
    ▼
[D. If] ── order_check == "NO"
    │  True  → [Recall] (quay lại hỏi tiếp thông tin thiếu)
    │  False → tiếp tục ↓
    ▼
[E. Bot API Call – Gọi AI Vector DB]
    │  Lấy thông tin chi tiết SP + giá từ Knowledge
    ▼
[F. Python Block – Tính tổng đơn hàng]
    │  Xử lý kết quả search, tính tổng giá
    │  Variable to save: order_summary
    ▼
[G. AI QnA – AI Chuyên trách xác nhận]
    │  Instruction: "Tổng hợp đơn hàng, báo giá, xin xác nhận"
    │  Input: {{order_summary}}
    │  Variable to save: bot_confirm_reply
    ▼
[H. Bot Send Text] ── {{bot_confirm_reply}}
    ▼
[I. AI QnA – AI Phân tích xác nhận]
    │  Output: {"action": "CONFIRM|CHANGE|CANCEL"}
    ▼
[J. Parallel]
    ├── CONFIRM → [Bot API Call] POST Contact list (xem mục 6.6)
    │            → [Bot Send Text] "Đơn hàng đã được ghi nhận..."
    │            → [Python Block] Xóa session.extra.cart + lịch sử chat đơn cũ
    │            → [Clear Topic]
    ├── CHANGE  → [Recall] (quay lại chỉnh sửa)
    └── CANCEL  → [Bot Send Text: cảm ơn] → [Clear Topic]
```

#### Flow 6: Nhân sự nội bộ (internal_staff)
```
[AI QnA – Hỏi xác thực]
    │  Instruction: "Hỏi mã nhân viên và bộ phận để xác thực"
    │  Enable JSON Mode: ON
    │  Output: {"employee_id":"...", "department":"..."}
    │  Variable to save: ai_auth_reply
    ▼
[Set Var] ── auth_info = json.loads(ai_auth_reply)
    ▼
[If] ── auth_info.employee_id != "" AND auth_info.department != ""
    ├── True  → [AI QnA Chuyên trách nội bộ]
    │             Enable Knowledge Aware: ON (Knowledge: Product FULL + Phác đồ)
    │             Instruction: "Trả lời thông tin nội bộ cho nhân viên VHN"
    │           → [Filter Bot Reply]
    │           → [Clear Topic]
    └── False → [Bot Send Text] "Vui lòng cung cấp mã nhân viên và bộ phận 
                  để em xác thực trước khi hỗ trợ ạ."
                (Không Clear Topic → giữ trong luồng chờ cung cấp)
```

#### Flow 7: Gọi hỗ trợ (handover)
```
[AI QnA – AI Phân tích]
    │  Instruction: "Trích xuất lý do cần hỗ trợ và thông tin khách"
    │  Enable JSON Mode: ON
    │  Output: {"reason":"...", "customer_name":"...", "phone":"..."}
    │  Variable to save: ai_handover_reply
    ▼
[Set Var] ── handover_info = json.loads(ai_handover_reply)
    ▼
[Bot API Call] ── POST API tạo ticket hỗ trợ (hoặc gửi thông báo)
    │  Body: {"reason": "{{handover_info.reason}}", 
    │         "name": "{{handover_info.customer_name}}",
    │         "bot_uuid": "{{bot_uuid}}", "thread_id": "{{thread_id}}"}
    ▼
[Bot Send Text] ── "Dạ, em đã chuyển yêu cầu của Anh/Chị cho bộ phận hỗ trợ. 
                     Nhân viên sẽ liên hệ lại trong thời gian sớm nhất ạ!"
    ▼
[Clear Topic]
```

---

## 4. KẾ HOẠCH TRIỂN KHAI TỪNG GIAI ĐOẠN

> **Chiến lược cuốn chiếu (theo lời khuyên sếp):**
> 1. Cấu hình AI đọc hiểu sheet **Company** + **QnA** trước → nền tảng kiến thức chung
> 2. Huấn luyện AI nhận diện và phân luồng B2B/B2C → test bằng câu mẫu
> 3. Đưa 14 SP thử nghiệm vào → test đề xuất đúng đối tượng → rồi mới nạp 240+ SP

### GIAI ĐOẠN 1: Chuẩn bị dữ liệu & Nền tảng kiến thức (Ngày 1-3)

| Bước | Công việc | Chi tiết | Ưu tiên |
|------|-----------|----------|---------|
| 1.1 | Làm sạch data Product | Chuẩn hóa vendor name Floslek, xử lý 66 SP thiếu giá → ghi "LIÊN HỆ", chuẩn hóa format giá | CAO |
| 1.2 | Tạo Knowledge Bank (xem mục 5.2) | Tạo 3 Book (General, B2B, B2C) + 1 QnA Library | CAO |
| 1.3 | **Nạp Company + QnA trước (Bước 1 cuốn chiếu)** | Sheet Company + QnA 237 cặp → nền tảng kiến thức chung | CAO |
| 1.4 | Nạp General Knowledge | Sheet Giới thiệu 7 nhãn hàng + Chính sách (nếu có) | CAO |
| 1.5 | Nạp Knowledge Product B2B | Lọc 98 SP (is_salon_product=True) + Phác đồ Christina | CAO |
| 1.6 | Nạp Knowledge Product B2C | Lọc 142 SP (is_salon_product=False) | CAO |
| 1.7 | Quick Test Knowledge | Test thử truy vấn trên từng Book/Library | CAO |
| 1.8 | Bổ sung dữ liệu thiếu | Yêu cầu VHN bổ sung: USP, chính sách bán hàng/vận chuyển/đổi trả | TRUNG BÌNH |
| 1.9 | Tạo tài khoản Conductify | Tạo 1 Admin + 3 Member theo sheet Account | CAO |

### GIAI ĐOẠN 2: Thiết kế Mindflow cơ bản & Phân luồng (Ngày 4-7)

| Bước | Công việc | Chi tiết |
|------|-----------|----------|
| 2.1 | Tạo Agent mới (xem mục 5.1) | Name: "Y Dược VHN Assistant", Avatar, Description |
| 2.2 | Cấu hình Session Manager (xem mục 6.1) | Extra fields JSON cho tất cả biến cần lưu |
| 2.3 | Thiết kế Router (xem mục 6.2) | 10 topics + Phrases cho mỗi topic |
| 2.4 | Xây Flows Switch | 10 flow, mỗi flow gán đúng 1 topic tương ứng |
| 2.5 | Xây Flow Chào hỏi | AI QnA + Knowledge General + QnA + Filter Bot Reply + Clear Topic |
| 2.6 | Xây Flow Off-topic | AI QnA hướng khách quay lại chủ đề + Clear Topic |
| 2.7 | Xây Flow Thông tin chung | AI QnA + Knowledge General → trả lời về VHN |
| 2.8 | Xây Flow Giới thiệu nhãn hàng | AI QnA + Knowledge General → giới thiệu 7 nhãn |
| 2.9 | Xây Flow Khuyến mãi | AI QnA + Knowledge General |
| 2.10 | **Xây Flow Sàng lọc B2B/B2C** | AI Phân tích + JSON Mode + Set Var + Parallel + Set Topic + Recall |
| 2.11 | **Test phân luồng (Bước 2 cuốn chiếu)** | Test bằng câu mẫu sếp: "Mình muốn mua sỉ cho spa" vs "Da mình nhạy cảm lắm tư vấn giúp mình" → xem Router phân đúng |

### GIAI ĐOẠN 3: Xây dựng luồng tư vấn chuyên sâu (Ngày 8-14)

| Bước | Công việc | Chi tiết |
|------|-----------|----------|
| 3.1 | Xây Flow B2B (xem Flow 3) | AI QnA + Knowledge B2B + Phác đồ + AI Phân tích JSON + Bot API Call thu lead |
| 3.2 | Xây Flow B2C (xem Flow 4) | AI QnA + Knowledge B2C + Guardrails + AI Phân tích + Set Topic order |
| 3.3 | Xây Flow Nội bộ (xem Flow 6) | AI Phân tích JSON xác thực Mã NV + If + AI QnA Knowledge Full |
| 3.4 | Xây Flow Đặt hàng (xem Flow 5) | Theo mẫu Buổi 11: AI Tổng quản → Python check → API → Tính toán → Ghi nhận |
| 3.5 | Xây Flow Handover (xem Flow 7) | AI Phân tích JSON + Bot API Call tạo ticket |
| 3.6 | Cấu hình Constants (xem mục 6.5) | Tên AI, tên công ty, hotline, email, mẫu câu missing price |
| 3.7 | Cấu hình Filter Bot Reply (xem mục 6.8) | Thay thế xưng hô, thuật ngữ |
| 3.8 | Cấu hình xử lý Missing Data | Mẫu câu khi SP thiếu giá/ảnh trong Instruction Prompt |

### GIAI ĐOẠN 4: Test, tinh chỉnh & Triển khai (Ngày 15-21)

| Bước | Công việc | Chi tiết |
|------|-----------|----------|
| 4.1 | **Nạp 14 SP thử nghiệm (Bước 3 cuốn chiếu)** | Đưa 14 SP từ PHẦN 1 yêu cầu sếp vào Knowledge → AI học cách đề xuất đúng SP cho đúng đối tượng |
| 4.2 | Test toàn bộ luồng với 14 SP (xem mục 7) | Chạy qua mọi kịch bản, dùng Testing Playground + Show Raw Output |
| 4.3 | Test Guardrails | Thử hỏi SP B2B (Step 3 Probiotic Peel) với tư cách khách B2C → AI phải từ chối |
| 4.4 | Test Missing Data | Hỏi SP thiếu giá → AI phải dùng mẫu câu sếp (xin SĐT) |
| 4.5 | Test Nội bộ | Hỏi "Liệt kê SP key dòng Unstress" → AI phải yêu cầu Bộ phận + Mã NV |
| 4.6 | **Nạp toàn bộ 240+ SP** | Sau khi 14 SP chạy mượt mà → nạp full vào Knowledge |
| 4.7 | Test lại với full data | Quick Test trên Knowledge + test end-to-end |
| 4.8 | Deploy to Production | Xuất bản AI Agent trên Conductify Studio |
| 4.9 | Tích hợp đa kênh (xem mục 8) | Integration Browser → Zalo + Facebook Messenger |
| 4.10 | Bàn giao AI CRM (xem mục 8) | Hướng dẫn VHN sử dụng Manual mode, Q&A, Contact list |

---

## 5. HƯỚNG DẪN CHI TIẾT TỪNG BƯỚC TRÊN CONDUCTIFY STUDIO

### 5.1. Bước 1: Tạo Agent mới

1. Đăng nhập Conductify AI Studio tại https://conductify.ai/
2. Vào mục **AI Agents** ở sidebar trái
3. Bấm nút **"+ Create"** để tạo Agent mới
4. Điền thông tin:
   - **Name:** `Y Dược VHN Assistant`
   - **Description:** `AI Sales Agent tư vấn dược mỹ phẩm quốc tế & giải pháp da liễu thẩm mỹ cho Công ty Y Dược VHN. Hỗ trợ khách hàng B2B (Spa, Clinic, Bệnh viện) và B2C (khách lẻ).`
5. Chọn **Create** → Agent mới hiển thị trên giao diện
6. Click vào Agent vừa tạo → mở giao diện **Mindflow** gồm 4 khu vực:
   - Khu vực Mindflow (kéo thả block)
   - Testing Playground (test trực tiếp)
   - Block Library (thư viện block)
   - Agent Profile (thông tin Agent)

### 5.2. Bước 2: Tạo Knowledge Bank

#### 5.2.1. Tạo General Knowledge (3 Book)

Vào mục **Knowledges** ở sidebar → tab **General Knowledge** → **Create new Book** cho từng Book:

**Book 1: `vhn_general_info`**

| Trường | Giá trị |
|--------|---------|
| Book Name | `vhn_general_info` |
| Access | Only me |
| AI Content Analyser | **VnEm** (vì nội dung tiếng Việt) |

Sau khi tạo → tab **Datasources** → **Add new datasource**:

| Datasource | Source format | Nội dung |
|-----------|---------------|---------|
| `vhn_company` | Text | Copy nội dung từ sheet Company (loại bỏ các dòng "Điền thông tin tại đây") |
| `vhn_brands` | Text | Copy nội dung từ sheet "Giới thiệu 7 nhãn hàng" – gồm Key giới thiệu + Key tư vấn của Christina, Ivatherm, Floslek, Dermoaroma, Preime, Pharmalife |
| `vhn_policies` | Text | Chính sách bán hàng/vận chuyển/đổi trả (cần VHN bổ sung) |

Cho mỗi datasource: giữ mặc định **Content Splitter**, **Maximum Segment Length**, **Overlap** → chọn **Save & Process** → đợi xử lý → **Reload list**.

**Sau khi nạp:** Vào tab **Datasources** → click vào từng datasource → kiểm tra phần **Text** xem nội dung có đầy đủ không. Nếu thiếu thông tin hình ảnh/bảng biểu → bổ sung mô tả bằng văn bản vào Text.

**Book 2: `vhn_b2b_product`**

| Trường | Giá trị |
|--------|---------|
| Book Name | `vhn_b2b_product` |
| Access | Only me |
| AI Content Analyser | **VnEm** |

Datasources:

| Datasource | Nội dung |
|-----------|---------|
| `b2b_products` | Lọc 98 SP có is_salon_product = True từ sheet Product. Format mỗi SP: `Tên SP \| Vendor \| Giá: XXX VNĐ \| Mô tả: ... \| Dung tích: ...` |
| `phac_do_christina` | Copy từ sheet "Phác đồ Christina" – 85 dòng phác đồ BioPhyto, Unstress, v.v. |
| `phac_do_christina_may` | Copy từ sheet "Phác đồ Christina + Máy" – 73 dòng phối hợp máy công nghệ cao |

**Book 3: `vhn_b2c_product`**

| Trường | Giá trị |
|--------|---------|
| Book Name | `vhn_b2c_product` |
| Access | Only me |
| AI Content Analyser | **VnEm** |

Datasource:

| Datasource | Nội dung |
|-----------|---------|
| `b2c_products` | Lọc 142 SP có is_salon_product = False. Format tương tự Book B2B |

**Lưu ý quan trọng cho Product datasource:**
- SP thiếu giá (66 SP): Ghi rõ `Giá: LIÊN HỆ` (KHÔNG để trống, KHÔNG bịa giá)
- SP thiếu ảnh (73 SP): Không ghi trường link_image
- Dùng `full_description` làm mô tả chính (vì cột Công dụng/Chỉ định hầu hết trống)

#### 5.2.2. Tạo Q&A Library

Vào tab **Questions & Answers** → **Create new Q&A Library**:

| Trường | Giá trị |
|--------|---------|
| Q&A Library Name | `vhn_qna` |
| Access | Only me |
| Language Model | VnEm (cố định, không đổi được) |

**Nạp 237 cặp Q&A bằng Import CSV:**

1. Mở sheet QnA trong Excel → tạo file mới chỉ có 2 cột: `question` và `answer`
2. Xuất file với định dạng **CSV (UTF-8)**
3. Trong Q&A Library → chọn **Import from CSV**
4. Kéo thả file CSV → **Import** → **Confirm**
5. Chọn **Reload list** để hiển thị kết quả
6. Kiểm tra: đếm số cặp Q&A đã import = 237

#### 5.2.3. Kiểm tra Knowledge bằng Quick Test

Sau khi nạp xong dữ liệu, **BẮT BUỘC** kiểm tra từng Book và Q&A Library:

1. Vào Book/Library → tab **Quick Test**
2. Nhập câu hỏi test → thiết lập **Limit = 3** → chọn **Test question**
3. Kiểm tra kết quả bên phải – xem AI có truy xuất đúng thông tin không

**Câu hỏi test mẫu:**

| Test trên | Câu hỏi | Kỳ vọng kết quả |
|-----------|---------|------------------|
| `vhn_general_info` | "Công ty VHN ở đâu?" | Trả về địa chỉ VP HCM + HN |
| `vhn_general_info` | "Christina là nhãn hàng gì?" | Trả về Key giới thiệu Christina |
| `vhn_b2b_product` | "Sản phẩm trị mụn cho spa" | Trả về SP B2B liên quan mụn |
| `vhn_b2c_product` | "Kem dưỡng da ban đêm" | Trả về SP B2C kem đêm |
| `vhn_b2b_product` | "Phác đồ Unstress" | Trả về phác đồ Unstress từ Christina |
| `vhn_qna` | "Giao hàng bao lâu?" | Trả về Q&A về thời gian giao hàng |
| `vhn_qna` | "Có ship COD không?" | Trả về Q&A về phương thức thanh toán |

Nếu kết quả không chính xác → kiểm tra lại nội dung datasource, bổ sung/chỉnh sửa và **Save & Process** lại.

#### 5.2.4. Lấy UUID để dùng trong Mindflow

Sau khi tạo xong và Quick Test OK:

1. **General Knowledge:** Vào mỗi Book → tab **Knowledge Book** → copy **Dataset UUID**
2. **Q&A Library:** Vào Library → tab **Q&A Settings** → copy **Dataset QnA UUID**

Ghi lại bảng UUID:

| Loại | Tên | UUID | Dùng cho Flow |
|------|-----|------|---------------|
| Book | vhn_general_info | (copy từ Studio) | Chào hỏi, Thông tin chung, Nhãn hàng, Khuyến mãi |
| Book | vhn_b2b_product | (copy từ Studio) | Tư vấn B2B, Nội bộ |
| Book | vhn_b2c_product | (copy từ Studio) | Tư vấn B2C |
| QnA | vhn_qna | (copy từ Studio) | Tất cả các flow có AI QnA |

### 5.3. Bước 3: Thiết kế Mindflow

Quay lại Agent → mở giao diện **Mindflow**. Thực hiện lần lượt theo mục 6.

---

## 6. CHI TIẾT KỸ THUẬT MINDFLOW

### 6.1. Cấu hình Session Manager – Extra Fields

Click vào block **Session Manager** (block đầu tiên) → thêm JSON vào khung **Extra Fields**:

```json
{
  "customer_type": "",
  "customer_name": "",
  "customer_phone": "",
  "customer_address": "",
  "facility_name": "",
  "facility_type": "",
  "skin_type": "",
  "skin_concern": "",
  "age_range": "",
  "cart": "[]",
  "employee_id": "",
  "employee_dept": "",
  "consultation_stage": "",
  "chat_history_b2b": "",
  "chat_history_b2c": ""
}
```

**Cách gọi biến ở block khác:** `{{ session.extra.customer_type }}`, `{{ session.extra.cart }}`, v.v.

**Kiểm tra:** Chọn **Show Raw Output** → nhắn thử 1 câu ở Testing Playground → xem Raw Output có hiển thị các biến session không.

### 6.2. Cấu hình Router – Topics, Phrases & Keywords

Click vào block **Router** → thêm lần lượt từng topic bằng nút **Add topic**:

#### Danh sách 10 topic và Phrases

**Topic 1: `greetings`**
```
Phrases:
- xin chào
- hello
- hi
- chào bạn
- chào shop
- alo
- có ai không
- shop ơi
```

**Topic 2: `off_topic`**
```
Phrases:
- thời tiết hôm nay thế nào
- bóng đá tối nay ai đá
- kể chuyện cười đi
- bạn có người yêu chưa
- nói về chính trị đi
```

**Topic 3: `company_info`**
```
Phrases:
- công ty VHN ở đâu
- địa chỉ cửa hàng
- số hotline bao nhiêu
- giờ làm việc của công ty
- liên hệ VHN qua đâu
- email công ty là gì
- văn phòng ở Hà Nội chỗ nào
```

**Topic 4: `brand_info`**
```
Phrases:
- Christina là nhãn hàng gì
- giới thiệu về Ivatherm
- Floslek có những dòng sản phẩm nào
- Dermoaroma là thương hiệu nước nào
- Preime có tốt không
- Pharmalife bán gì
- các nhãn hàng VHN phân phối
- thương hiệu nào tốt nhất
```

**Topic 5: `b2b_consult`** *(Dấu hiệu nhận biết B2B – PHẦN 2 mục 2)*
```
Phrases:
- mình muốn mua sỉ cho spa
- tôi cần sản phẩm cho thẩm mỹ viện
- bảng giá đại lý bao nhiêu
- chiết khấu cho đại lý là bao nhiêu
- spa muốn nhập hàng
- sản phẩm cho bệnh viện da liễu
- tôi là chủ nhà thuốc muốn tìm hiểu
- step trị liệu chuyên nghiệp
- phác đồ điều trị da mụn cho spa
- sản phẩm chuyên dùng trong phòng khám
- sản phẩm cho clinic
- mua sỉ sản phẩm Christina
```

> **Dấu hiệu B2B (theo sếp):** Khách nhắc đến Spa, Thẩm mỹ viện, Clinic, Bệnh viện, Nhà thuốc, Đại lý; hỏi chiết khấu, mua sỉ, bảng giá đại lý, các bước trị liệu chuyên nghiệp (Step 1-10).

**Topic 6: `b2c_consult`** *(Dấu hiệu nhận biết B2C – PHẦN 2 mục 2)*
```
Phrases:
- da mình bị mụn tư vấn giúp
- kem dưỡng da nào tốt
- mình da nhạy cảm dùng gì
- routine chăm sóc da buổi tối
- mình muốn mua kem chống nắng
- sản phẩm trị nám cho da
- tư vấn sản phẩm cho da dầu
- mình muốn mua sản phẩm dùng tại nhà
- mua lẻ sản phẩm được không
- da mình bị lão hóa dùng gì
- tư vấn routine chăm sóc da tại nhà
```

> **Dấu hiệu B2C (theo sếp):** Khách hỏi mua lẻ, hỏi giá 1 SP cụ thể để tự dùng; mô tả tình trạng da cá nhân (da mụn, da nám, da nhạy cảm); cần tư vấn routine chăm sóc da tại nhà.

**Topic 7: `order`**
```
Phrases:
- mình muốn đặt hàng
- chốt đơn giúp mình
- mình lấy sản phẩm đó
- mua luôn
- thêm vào giỏ hàng
- thanh toán như nào
- giao hàng về đâu
```

**Topic 8: `internal_staff`** *(Luồng bảo mật nội bộ – PHẦN 2 mục 2)*
```
Phrases:
- tôi là nhân viên công ty
- liệt kê sản phẩm key của dòng Unstress
- báo cáo số lượng sản phẩm
- thông tin nội bộ
- danh sách sản phẩm theo vendor
- mã nhân viên của tôi là
```

> **Theo sếp (sheet Kịch bản bán hàng dòng 94-96):** Nếu người dùng hỏi câu hỏi nội bộ (VD: "Liệt kê các sản phẩm key của dòng Unstress"), AI phải yêu cầu cung cấp **Bộ phận và Mã số nhân viên** trước khi trả lời.

**Topic 9: `handover`**
```
Phrases:
- cho mình gặp quản lý
- tôi muốn khiếu nại
- không hài lòng với sản phẩm
- gọi nhân viên hỗ trợ
- cần nói chuyện với người thật
- yêu cầu hỗ trợ trực tiếp
```

**Topic 10: `promotion`**
```
Phrases:
- có khuyến mãi gì không
- chương trình giảm giá
- voucher ưu đãi
- mua 1 tặng 1 không
- đang có sale gì không
```

> **Lưu ý (theo tài liệu Mindflow v1.0):**
> - Ưu tiên dùng **Phrases** (câu tự nhiên), hạn chế dùng Keywords
> - Tên topic viết liền không dấu
> - Nên có ít nhất 5-10 phrases cho mỗi topic để AI Tổng quản phân loại chính xác

### 6.2.1. Cấu hình Flows Switch

Click vào block **Flows Switch** → tạo 10 flow bằng nút **Add Flow**:

| Flow name | Topic gán | Cách gán |
|-----------|-----------|----------|
| `greetings` | greetings | Click mũi tên ở "Available Topics can use" |
| `off_topic` | off_topic | Tương tự |
| `company_info` | company_info | Tương tự |
| `brand_info` | brand_info | Tương tự |
| `b2b_consult` | b2b_consult | Tương tự |
| `b2c_consult` | b2c_consult | Tương tự |
| `order` | order | Tương tự |
| `internal_staff` | internal_staff | Tương tự |
| `handover` | handover | Tương tự |
| `promotion` | promotion | Tương tự |

> **Quy tắc TUYỆT ĐỐI (theo tài liệu Mindflow v1.0):**
> - Mỗi flow gán đúng 1 topic (để kết quả tốt nhất)
> - TUYỆT ĐỐI không nhập topic không có ở Router
> - TUYỆT ĐỐI không để trống Topics trong bất kỳ flow nào

### 6.3. Instruction Prompt – Flow B2B

Dán vào trường **Instruction Prompt** của block AI QnA trong flow `b2b_consult`:

```
# Vai trò
Bạn là Chuyên viên tư vấn da liễu và chăm sóc khách hàng đại diện cho Công ty Y dược VHN.

# Giọng điệu
Chuyên nghiệp, lịch sự, chuẩn y khoa, tận tâm và đáng tin cậy.

# Đối tượng
Khách hàng B2B: Spa, Thẩm mỹ viện, Clinic, Bệnh viện, Nhà thuốc, Đại lý.

# Quy trình tư vấn B2B (theo Flowchart sếp – PHẦN 3)
Bước 1: Hỏi tên khách để tiện xưng hô.
Bước 2: Hỏi tên cơ sở (Spa/Clinic/Bệnh viện/Nhà thuốc), khu vực hoạt động.
Bước 3: Hỏi dịch vụ chính đang cung cấp (trị mụn, làm trắng, phục hồi da, chống lão hóa...).
Bước 4: Hỏi thiết bị công nghệ cao đang sử dụng (nếu có).
Bước 5: Dựa vào nhu cầu, giới thiệu dòng sản phẩm chuyên nghiệp phù hợp. CHỈ giới thiệu sản phẩm có is_salon_product = True. Nhấn mạnh hiệu quả trị liệu lâm sàng và uy tín thương hiệu (Christina phân phối tại hơn 2000 bệnh viện/spa).
Bước 6: Nếu khách hỏi về phác đồ điều trị, truy xuất từ Knowledge để giới thiệu phác đồ chuyên nghiệp.
Bước 7: Khi khách hỏi chiết khấu/giá sỉ, trả lời: "Dạ, chính sách đại lý sẽ được chuyên viên kinh doanh tư vấn trực tiếp cho Anh/Chị ạ. Anh/Chị vui lòng cho em xin Tên, SĐT và tên cơ sở để em chuyển cho bộ phận kinh doanh liên hệ hỗ trợ ạ!"
Bước 8: Thu thập đầy đủ: Tên + SĐT + Tên cơ sở (Spa/Clinic) + Địa chỉ → chuyển cho bộ phận Sales.

# Mục tiêu Conversion (theo yêu cầu sếp – PHẦN 2 mục 5)
Kết thúc bằng việc xin Tên + SĐT + Tên cơ sở (Spa/Clinic) + Địa chỉ để chuyển cho bộ phận Sales liên hệ tư vấn chính sách đại lý.

# Quy tắc NGHIÊM NGẶT (Guardrails – PHẦN 2 mục 3)
- CHỈ giới thiệu sản phẩm chuyên nghiệp (is_salon_product = True). TUYỆT ĐỐI KHÔNG giới thiệu sản phẩm homecare (is_salon_product = False) cho khách B2B.
- KHÔNG bịa giá sỉ, chiết khấu. Nếu khách hỏi giá sỉ → xin thông tin để chuyển Sales. Bảo mật giá sỉ: chỉ cung cấp giá bán lẻ niêm yết.
- KHÔNG tiết lộ thông tin nội bộ công ty.
- Nếu sản phẩm thiếu giá (Missing Data – PHẦN 2 mục 4): "Dạ, sản phẩm [Tên sản phẩm] hiện đang có chương trình ưu đãi đặc biệt dành riêng cho từng thời điểm. Anh/Chị vui lòng để lại SĐT để em báo giá chính xác nhất kèm quà tặng kèm theo cho mình nhé ạ!"
- Nếu sản phẩm thiếu ảnh: CHỈ mô tả bằng lời, KHÔNG gửi link ảnh không tồn tại.
- KHÔNG tự bịa thông tin sản phẩm không có trong Knowledge (không hallucination).
- Trả lời ngắn gọn, dưới 80 từ mỗi lượt.
- Xưng hô: "Dạ", "em", "Anh/Chị". KHÔNG xưng "tôi", "mình".
```

**Cấu hình block AI QnA cho flow B2B:**

| Trường | Giá trị |
|--------|---------|
| Name | `AI_B2B_Consultant` |
| Enable Knowledge Aware | ✅ ON |
| Knowledge Dataset UUID | (paste UUID của Book `vhn_b2b_product`) |
| Knowledge Dataset QA UUID | (paste UUID của Library `vhn_qna`) |
| Knowledge Result Limit | `3` |
| Enable Chat History Aware | ✅ ON |
| Enable Human Input Aware | ✅ ON |
| Variable to save AI reply | `bot_b2b_reply` |
| Temperature | `0.7` |
| Max Tokens | `500` |
| AI Model | `GPT-4o-mini` (hoặc GPT-4 nếu cần chất lượng cao hơn) |

### 6.4. Instruction Prompt – Flow B2C

```
# Vai trò
Bạn là Chuyên viên tư vấn da liễu và chăm sóc khách hàng đại diện cho Công ty Y dược VHN.

# Giọng điệu
Chuyên nghiệp, lịch sự, chuẩn y khoa, tận tâm và đáng tin cậy.

# Đối tượng
Khách hàng cá nhân muốn mua sản phẩm chăm sóc da tại nhà.

# Quy trình tư vấn B2C (theo Flowchart sếp – PHẦN 3)
Bước 1: Hỏi tên khách để tiện xưng hô.
Bước 2: Hỏi loại da (da dầu, da khô, da hỗn hợp, da nhạy cảm).
Bước 3: Hỏi độ tuổi.
Bước 4: Hỏi tình trạng da hiện tại (mụn, nám, lão hóa, nhạy cảm, thâm, sần sùi...).
Bước 5: Hỏi tình trạng đặc biệt (có thai, cho con bú, đang stress...).
Bước 6: Hỏi thói quen skincare hiện tại.
Bước 7: Đề xuất routine phù hợp với sản phẩm homecare B2C (is_salon_product = False). Giải thích công dụng chính, cách dùng, và báo giá bán lẻ niêm yết.
Bước 8: Thuyết phục khách về hiệu quả phục hồi/điều trị của sản phẩm.
Bước 9: Khi khách sẵn sàng → chuyển sang luồng đặt hàng.

# Mục tiêu Conversion (theo yêu cầu sếp – PHẦN 2 mục 5)
Kết thúc bằng việc hướng dẫn khách chốt đơn, xin Tên + SĐT + Địa chỉ giao hàng để lên đơn bán lẻ.

# Quy tắc NGHIÊM NGẶT (Guardrails – PHẦN 2 mục 3)
- CHỈ đề xuất sản phẩm homecare (is_salon_product = False).
- TUYỆT ĐỐI KHÔNG đề xuất sản phẩm B2B (Step trị liệu chuyên nghiệp, peel mạnh như Step 3 Probiotic Peel) cho khách tự dùng tại nhà → tránh gây kích ứng/tổn thương da. Nếu khách hỏi SP B2B, giải thích: "Dạ, sản phẩm này là dòng chuyên nghiệp cần thực hiện tại Spa/Clinic bởi chuyên gia ạ. Em xin tư vấn sản phẩm homecare phù hợp cho Anh/Chị nhé!"
- Nếu sản phẩm thiếu giá (Missing Data – PHẦN 2 mục 4): "Dạ, sản phẩm [Tên sản phẩm] hiện đang có chương trình ưu đãi đặc biệt dành riêng cho từng thời điểm. Anh/Chị vui lòng để lại SĐT để em báo giá chính xác nhất kèm quà tặng kèm theo cho mình nhé ạ!"
- Nếu sản phẩm thiếu ảnh: CHỈ mô tả bằng lời, KHÔNG gửi link ảnh trống.
- KHÔNG bịa giá, KHÔNG bịa thông tin sản phẩm không có trong Knowledge (không hallucination).
- Trả lời ngắn gọn, dưới 80 từ mỗi lượt.
- Xưng hô: "Dạ", "em", "Anh/Chị". KHÔNG xưng "tôi", "mình".
```

**Cấu hình block AI QnA cho flow B2C:**

| Trường | Giá trị |
|--------|---------|
| Name | `AI_B2C_Consultant` |
| Enable Knowledge Aware | ✅ ON |
| Knowledge Dataset UUID | (paste UUID của Book `vhn_b2c_product`) |
| Knowledge Dataset QA UUID | (paste UUID của Library `vhn_qna`) |
| Knowledge Result Limit | `3` |
| Enable Chat History Aware | ✅ ON |
| Enable Human Input Aware | ✅ ON |
| Variable to save AI reply | `bot_b2c_reply` |
| Temperature | `0.7` |
| Max Tokens | `500` |
| AI Model | `GPT-4o-mini` |

### 6.5. Cấu hình Constants

Trong Mindflow, sử dụng block **Set Const** để thiết lập các hằng số dùng chung:

| Tên hằng số | Giá trị | Cú pháp gọi |
|-------------|---------|--------------|
| `const_ai_name` | `Thảo Vi` | `{{const_ai_name}}` |
| `const_company_name` | `Y Dược VHN` | `{{const_company_name}}` |
| `const_company_full` | `Công ty CP XNK & Phân Phối Sản Phẩm Y Dược VHN` | `{{const_company_full}}` |
| `const_hotline` | `0941 905 885` | `{{const_hotline}}` |
| `const_email` | `truongphongmarketing@vhndistribution.com` | `{{const_email}}` |
| `const_website` | `vhndistribution.com` | `{{const_website}}` |
| `const_shopee` | `https://shopee.vn/yduocvhn` | `{{const_shopee}}` |
| `const_missing_price_msg` | (xem bên dưới) | `{{const_missing_price_msg}}` |

**Mẫu câu khi SP thiếu giá (theo sếp – PHẦN 2 mục 4):**
```
Dạ, sản phẩm [Tên sản phẩm] hiện đang có chương trình ưu đãi đặc biệt dành riêng cho từng thời điểm. Anh/Chị vui lòng để lại SĐT để em báo giá chính xác nhất kèm quà tặng kèm theo cho mình nhé ạ!
```

### 6.6. API Ghi nhận đơn hàng / Lead

**Endpoint:** `POST https://api.workerbot.ai/v1/contact-list/create`

Sử dụng block **Bot API Call** trong Mindflow:
- **Method:** POST
- **URL:** `https://api.workerbot.ai/v1/contact-list/create`

**Raw Body cho B2C (đơn hàng):**
```json
{
  "name": "{{session.extra.customer_name}}",
  "phone": "{{session.extra.customer_phone}}",
  "address": "{{session.extra.customer_address}}",
  "company": "",
  "email": "",
  "bot_uuid": "{{bot_uuid}}",
  "thread_id": "{{thread_id}}",
  "full_field": {
    "type": "B2C_ORDER",
    "products": "{{session.extra.cart}}",
    "total_price": "{{order_total}}",
    "note": ""
  }
}
```

**Raw Body cho B2B (lead):**
```json
{
  "name": "{{session.extra.customer_name}}",
  "phone": "{{session.extra.customer_phone}}",
  "address": "{{session.extra.customer_address}}",
  "company": "{{session.extra.facility_name}}",
  "email": "",
  "bot_uuid": "{{bot_uuid}}",
  "thread_id": "{{thread_id}}",
  "full_field": {
    "type": "B2B_LEAD",
    "facility_type": "{{session.extra.facility_type}}",
    "interest": "{{b2b_info.interest}}",
    "note": ""
  }
}
```

> **Lưu ý (theo Buổi 11 – mục 4.4.4):**
> - `bot_uuid` và `thread_id` là **system variables**, lấy trực tiếp từ Mindflow, không cần tự tạo
> - Các biến khác có thể dùng **AI Phân tích** JSON Mode để trích xuất
> - Trường `full_field` có giá trị là JSON, thêm/bớt field tùy mục đích

### 6.7. Python Block – Lưu chat history vào Session Extra

Dùng block **Python** (không phải Python Expression) trong flow B2B/B2C để lưu lịch sử hội thoại:

```python
import json

current_history = "{{session.extra.chat_history_b2b}}"
new_message = "{{human_input}}"
ai_reply = "{{bot_b2b_reply}}"

if current_history:
    history = current_history + "\nUser: " + new_message + "\nAI: " + ai_reply
else:
    history = "User: " + new_message + "\nAI: " + ai_reply

print(history)
```

**Variable to save:** `updated_history`

Sau đó dùng **Set Var** để gán lại: `session.extra.chat_history_b2b = updated_history`

### 6.8. Cấu hình Filter Bot Reply

Đặt block **Filter Bot Reply** sau block AI QnA trong mỗi flow:

> **Điều kiện (theo tài liệu Mindflow v1.0):** PHẢI có block AI QnA phía trước. Filter Bot Reply chỉ hoạt động trên output của AI QnA.

| # | Regex | Replace | Mục đích |
|---|-------|---------|----------|
| 1 | `(?:trợ lý ảo\|chatbot\|bot\|AI)` | `tư vấn viên` | Tránh AI tự gọi mình là bot |
| 2 | `(?:Tôi\|tôi)` | `em` | Đúng cách xưng hô persona Thảo Vi |
| 3 | `(?:tôi không biết\|tôi không có thông tin)` | `em chưa có thông tin chi tiết về phần này` | Phản hồi chuyên nghiệp hơn |
| 4 | `(?:bạn\|Bạn)` | `Anh/Chị` | Xưng hô lịch sự |

### 6.9. Kỹ thuật đổi Topic + Recall (Flow Sàng lọc)

Theo hướng dẫn Buổi 9 (mục 3.5.1), kỹ thuật đổi topic sử dụng kết hợp:

1. **AI QnA** (AI Phân tích): Phân tích ý định thực sự của User → trả về JSON
2. **Set Var**: Parse JSON bằng `json.loads()`
3. **Parallel**: Rẽ nhánh theo giá trị customer_type
4. **Set Topic**: Đặt topic mới (b2b_consult / b2c_consult / internal_staff)
5. **Recall**: Chạy lại Mindflow với topic mới

> **Lưu ý QUAN TRỌNG:** KHÔNG đặt block Clear Topic ở flow dùng Recall. Nếu đặt Clear Topic trước Recall, topic sẽ bị xóa và Recall sẽ không hoạt động đúng.

**Instruction Prompt cho AI Phân tích sàng lọc (áp dụng logic sếp – PHẦN 2 mục 2):**
```
Phân tích câu nói của khách hàng và xác định họ thuộc nhóm nào:

- "b2b": Nếu khách nhắc đến Spa, Thẩm mỹ viện, Clinic, Bệnh viện, Nhà thuốc, Đại lý; hỏi chiết khấu, mua sỉ, bảng giá đại lý, các bước trị liệu chuyên nghiệp (Step 1-10).
- "b2c": Nếu khách hỏi mua lẻ, hỏi giá 1 sản phẩm cụ thể để tự dùng; mô tả tình trạng da cá nhân (da mụn, da nám, da nhạy cảm); cần tư vấn routine chăm sóc da tại nhà.
- "internal": Nếu khách hỏi câu hỏi mang tính nội bộ công ty (VD: "Liệt kê các sản phẩm key của dòng Unstress"), yêu cầu Mã nhân viên.
- "unclear": Nếu không thể xác định rõ ràng → hỏi khéo: "Dạ, không biết Anh/Chị đang cần tìm sản phẩm để chăm sóc da tại nhà hay dùng cho dịch vụ tại Spa/phòng khám của mình ạ?"

Trả lời ĐÚNG format JSON: {"customer_type": "b2b|b2c|internal|unclear"}
Chỉ trả lời JSON, không thêm gì khác.
```

**Cấu hình block AI QnA:**
- Enable JSON Mode: ✅ ON
- Enable Chat History Aware: ❌ OFF
- Enable Human Input Aware: ✅ ON
- Variable to save: `ai_screening_reply`
- Temperature: `0.3` (cần chính xác, giảm sáng tạo)
- AI Model: `GPT-4o-mini` (JSON Mode chỉ hoạt động với GPT)

---

## 7. KỊCH BẢN TEST & TIÊU CHÍ NGHIỆM THU

### 7.1. Cách test trên Conductify Studio

1. Mở Agent → giao diện Mindflow → phần **Testing Playground** bên phải
2. Bật **Show Raw Output** để xem chi tiết prompt và phản hồi từ từng block
3. Nhắn câu test → quan sát:
   - Router phân đúng topic không?
   - Flow nào được kích hoạt?
   - AI QnA có truy xuất đúng Knowledge không?
   - Biến có được set đúng giá trị không?
4. Kiểm tra **Raw Output from Mindflow Executor** để debug

### 7.2. Kịch bản test phân luồng

| # | Câu test | Kỳ vọng Router → Topic | Kỳ vọng Flow |
|---|----------|------------------------|--------------|
| 1 | "Mình muốn mua sỉ cho spa" | → b2b_consult | Tư vấn B2B |
| 2 | "Da mình nhạy cảm lắm, tư vấn giúp mình" | → b2c_consult | Tư vấn B2C |
| 3 | "Liệt kê các sản phẩm key của dòng Unstress" | → internal_staff | Nội bộ (yêu cầu Mã NV) |
| 4 | "Xin chào" | → greetings | Chào hỏi |
| 5 | "Công ty VHN ở đâu?" | → company_info | Thông tin chung |
| 6 | "Tôi muốn mua sản phẩm cho bệnh viện" | → b2b_consult | Tư vấn B2B |
| 7 | "Mình muốn mua kem dưỡng đêm để dùng" | → b2c_consult | Tư vấn B2C |
| 8 | "Bảng giá đại lý bao nhiêu?" | → b2b_consult | Tư vấn B2B |
| 9 | "Cho mình gặp quản lý" | → handover | Gọi hỗ trợ |
| 10 | "Christina là nhãn hàng gì?" | → brand_info | Giới thiệu nhãn hàng |
| 11 | "Có đang khuyến mãi gì không?" | → promotion | Khuyến mãi |
| 12 | "Cho mình đặt hàng" | → order | Đặt hàng |

### 7.3. Kịch bản test Guardrails

| # | Tình huống | Kỳ vọng | Cách kiểm tra |
|---|------------|---------|---------------|
| 1 | Khách B2C hỏi "Cho mình mua Step 3 Probiotic Peel" | AI từ chối, giải thích đây là SP chuyên nghiệp cần thực hiện tại Spa, gợi ý SP B2C thay thế | Xem AI QnA response trong Raw Output |
| 2 | Khách B2B hỏi "Giá sỉ bao nhiêu?" | AI từ chối báo giá sỉ, xin thông tin (Tên + SĐT + Tên cơ sở) để Sales liên hệ | Xem response |
| 3 | Hỏi SP thiếu giá (1 trong 66 SP) | AI dùng mẫu câu xin SĐT: "Dạ, sản phẩm... hiện đang có chương trình ưu đãi..." KHÔNG bịa giá | Kiểm tra response không chứa số tiền bịa |
| 4 | Hỏi nội bộ không cung cấp Mã NV | AI yêu cầu xác thực trước khi trả lời: "Vui lòng cung cấp mã nhân viên..." | Xem flow If rẽ nhánh đúng |
| 5 | Hỏi AI: "Bạn là ai?" | AI trả lời "em là chuyên viên tư vấn da liễu của Y dược VHN" (không nói "tôi là chatbot/AI") | Filter Bot Reply hoạt động |

### 7.4. Kịch bản test end-to-end

**Test B2C đầy đủ (cả luồng từ tư vấn → chốt đơn):**

| Bước | User nói | AI phải làm | Kiểm tra |
|------|----------|-------------|----------|
| 1 | "Chào shop" | Chào hỏi với persona chuyên viên tư vấn da liễu | Router → greetings, xưng "em" |
| 2 | "Da mình bị mụn, tư vấn giúp" | Router phân sang b2c_consult, hỏi loại da | Topic đổi đúng |
| 3 | "Da dầu" | Hỏi thêm: tuổi | Chat History Aware hoạt động |
| 4 | "28 tuổi, mới bị gần đây" | Hỏi thêm: tình trạng đặc biệt | AI theo đúng quy trình |
| 5 | "Không có gì đặc biệt" | Đề xuất routine + SP B2C phù hợp | Knowledge B2C truy xuất đúng, KHÔNG có SP B2B |
| 6 | "Mình lấy sản phẩm đó" | Chuyển sang luồng đặt hàng | Set Topic → order → Recall |
| 7 | Cung cấp Tên + SĐT + Địa chỉ | Tổng hợp đơn, xin xác nhận | Python check biến = YES |
| 8 | "Xác nhận" | Ghi nhận vào Contact list + cảm ơn | API call thành công, Clear Topic |

**Test B2B đầy đủ (tư vấn → thu lead):**

| Bước | User nói | AI phải làm | Kiểm tra |
|------|----------|-------------|----------|
| 1 | "Mình muốn mua sản phẩm cho spa" | Router → b2b_consult, hỏi thông tin cơ sở | Topic đúng |
| 2 | "Spa Beauty ở quận 3" | Hỏi dịch vụ chính | Chat History lưu đúng |
| 3 | "Trị mụn và phục hồi da" | Giới thiệu SP B2B phù hợp + phác đồ | Knowledge B2B truy xuất, KHÔNG có SP B2C |
| 4 | "Giá sỉ bao nhiêu?" | Từ chối báo giá, xin thông tin liên hệ | Guardrail hoạt động |
| 5 | "Nguyễn Văn A, 0912345678" | Ghi nhận lead vào Contact list | API call B2B_LEAD thành công |

### 7.5. Tiêu chí nghiệm thu

| Tiêu chí | Yêu cầu | Cách đo |
|-----------|----------|---------|
| Phân luồng chính xác | ≥ 90% câu test được Router phân đúng | Test 12 câu mẫu |
| Guardrails B2B↔B2C | 100% — Không bao giờ đề xuất SP B2B cho khách B2C | Test 5 kịch bản |
| Không hallucination | 100% — Không bịa giá, không bịa thông tin SP | Kiểm tra response vs Knowledge |
| Chốt đơn B2C | Ghi nhận thành công vào Contact list | Kiểm tra Contact list trên AI CRM |
| Thu lead B2B | Ghi nhận thành công vào Contact list | Kiểm tra Contact list trên AI CRM |
| Xác thực nội bộ | 100% — Luôn yêu cầu Mã NV trước khi trả lời | Test 2 lần |
| Xử lý missing data | 100% — Dùng đúng mẫu câu khi SP thiếu giá | Hỏi 3 SP thiếu giá khác nhau |
| Giọng điệu | Đúng persona: chuyên nghiệp, lịch sự, chuẩn y khoa, dạ/em, dưới 80 từ | Đọc 10 response |
| Filter Bot Reply | 100% — Không xuất hiện "trợ lý ảo", "tôi", "bạn" | Kiểm tra 10 response |

---

## 8. TRIỂN KHAI ĐA KÊNH & BÀN GIAO

### 8.1. Deploy to Production

Sau khi test thành công:
1. Trong giao diện Agent → chọn **Deploy to Production**
2. AI Agent sẽ được xuất bản và sẵn sàng tích hợp

### 8.2. Integration Browser – Tích hợp lên Zalo & Facebook

Theo hướng dẫn Buổi 11 (mục 4.3):

#### 8.2.1. Cài đặt Integration Browser
1. Tải về Integration Browser từ Conductify
2. Mở ứng dụng → trang **Profiles** xuất hiện
3. Chọn **Add** → nhập tên Profile (VD: `VHN_Zalo_1`) → **Create**

#### 8.2.2. Tích hợp lên Zalo
1. Chọn Profile vừa tạo
2. Đăng nhập Zalo trên Integration Browser
3. Cấu hình kết nối AI Agent → Zalo cá nhân hoặc OA
4. Test: Nhắn tin qua Zalo → AI Agent phản hồi

#### 8.2.3. Tích hợp lên Facebook Messenger
1. Tạo Profile mới (VD: `VHN_Facebook_1`)
2. Đăng nhập Facebook trên Integration Browser
3. Kết nối với Fanpage doanh nghiệp
4. Test: Nhắn tin qua Messenger → AI Agent phản hồi

### 8.3. Bàn giao AI CRM

Hướng dẫn VHN sử dụng AI CRM tại https://hub.conductify.ai/:

#### 8.3.1. Dashboard
- Đăng nhập → thấy AI Agent "Y Dược VHN Assistant" đã Published
- Biểu tượng bánh răng: quản lý Agent
- Nút OPEN: mở chat standalone để test

#### 8.3.2. Tab CRM – Quản lý hội thoại
- **Tìm kiếm:** Dùng filter theo kênh (Zalo/Facebook/Website), thời gian, Mode
- **Manual mode:** Bật khi AI chưa xử lý được → nhân viên tự nhắn cho khách
  - Tin nhắn phân loại: "Send by AI" vs "Send by Human"
  - Textbox nhập tay chỉ hiển thị khi bật Manual

#### 8.3.3. Tab Q&A – Chỉnh sửa kiến thức
- Điều chỉnh Q&A trực tiếp trên AI CRM mà không cần vào Studio
- Có thanh search, thêm mới, chỉnh sửa, xóa cặp Q&A

#### 8.3.4. Tab Integrations
- **Public URL:** Link chat standalone (nhúng vào website)
- **Web Embed:** Mã nhúng AI Agent vào website VHN

#### 8.3.5. Tab Contact list – Xem đơn hàng/Lead
- Xem tất cả đơn hàng B2C và lead B2B đã ghi nhận
- Các trường: STT, Ngày tạo, Tên, Email, SĐT, Địa chỉ, Công ty, Thông tin khác
- Hỗ trợ: tìm kiếm, phân trang, **xuất file CSV** để báo cáo

---

## 9. RỦI RO & GIẢI PHÁP

| # | Rủi ro | Mức độ | Giải pháp |
|---|--------|--------|-----------|
| 1 | 66 SP thiếu giá → AI bịa giá | CAO | Ghi "LIÊN HỆ" trong data + Guardrail trong prompt + Filter Bot Reply |
| 2 | AI đề xuất SP B2B cho khách B2C | CAO | Tách riêng 2 bộ Knowledge Book (B2B/B2C), instruction prompt nghiêm ngặt |
| 3 | Sheet Company thiếu chính sách | TRUNG BÌNH | Yêu cầu VHN bổ sung TRƯỚC khi triển khai GĐ 1 |
| 4 | Vendor name Floslek bị lỗi | THẤP | Làm sạch data trước khi nạp Knowledge |
| 5 | Router phân sai B2B/B2C khi câu hỏi mơ hồ | TRUNG BÌNH | Flow Sàng lọc hỏi lại "chăm sóc tại nhà hay cho dịch vụ Spa?" |
| 6 | Khách hỏi về combo nhưng cột combo trống | TRUNG BÌNH | AI dựa vào Knowledge gợi ý SP phối hợp, không phụ thuộc cột combo |
| 7 | Phác đồ trị liệu VHN (sheet riêng) trống | THẤP | Dùng Phác đồ Christina có sẵn (85 + 73 dòng), yêu cầu VHN bổ sung sau |
| 8 | JSON Mode chỉ hoạt động với GPT | TRUNG BÌNH | Dùng GPT-4o-mini cho các block cần JSON. Block tư vấn có thể dùng model khác |
| 9 | Knowledge truy xuất sai do data quá lớn | TRUNG BÌNH | Tách data theo category, tăng Knowledge Result Limit, dùng Quick Test kiểm tra |

---

## 10. CHECKLIST TỔNG HỢP

### Trước khi bắt đầu (yêu cầu VHN bổ sung)
- [ ] USP doanh nghiệp
- [ ] Chính sách bán hàng
- [ ] Chính sách vận chuyển
- [ ] Chính sách đổi trả / khiếu nại
- [ ] Chính sách bảo mật
- [ ] Hệ thống cửa hàng (nếu có)
- [ ] Email nhận thông báo đơn hàng / lead mới
- [ ] Tài khoản Conductify (1 Admin + 3 Member)
- [ ] Xác nhận nền tảng triển khai (Website / Zalo / Facebook)

### Giai đoạn 1 – Dữ liệu & Knowledge Bank
- [ ] Làm sạch vendor name Floslek (3 SP lỗi)
- [ ] Xử lý 66 SP thiếu giá → ghi "LIÊN HỆ"
- [ ] Chuẩn hóa format giá: "X,XXX,000 VNĐ"
- [ ] Tạo Book `vhn_general_info` (VnEm) + nạp 3 datasource
- [ ] Tạo Book `vhn_b2b_product` (VnEm) + nạp 3 datasource (SP B2B + 2 phác đồ)
- [ ] Tạo Book `vhn_b2c_product` (VnEm) + nạp 1 datasource (SP B2C)
- [ ] Tạo Q&A Library `vhn_qna` (VnEm) + Import 237 cặp từ CSV
- [ ] Quick Test trên `vhn_general_info` (3 câu test)
- [ ] Quick Test trên `vhn_b2b_product` (2 câu test)
- [ ] Quick Test trên `vhn_b2c_product` (2 câu test)
- [ ] Quick Test trên `vhn_qna` (2 câu test)
- [ ] Ghi lại bảng UUID (4 UUID: 3 Book + 1 QnA)

### Giai đoạn 2 – Mindflow cơ bản
- [ ] Tạo Agent "Y Dược VHN Assistant"
- [ ] Session Manager + Extra Fields (14 biến JSON)
- [ ] Router: 10 topics + phrases cho mỗi topic
- [ ] Flows Switch: 10 flow, mỗi flow gán 1 topic
- [ ] Flow Chào hỏi: AI QnA + Knowledge General + Filter + Clear Topic
- [ ] Flow Off-topic: AI QnA + Clear Topic
- [ ] Flow Thông tin chung: AI QnA + Knowledge General + Filter + Clear Topic
- [ ] Flow Giới thiệu nhãn hàng: AI QnA + Knowledge General + Filter + Clear Topic
- [ ] Flow Khuyến mãi: AI QnA + Knowledge General + Filter + Clear Topic
- [ ] Flow Sàng lọc: AI Phân tích JSON + Set Var + Parallel + Set Topic + Recall
- [ ] Test phân luồng: 12 câu test (Show Raw Output)

### Giai đoạn 3 – Luồng chuyên sâu
- [ ] Flow B2B: AI QnA (Knowledge B2B) + Filter + Python + AI Phân tích JSON + Parallel + Bot API Call
- [ ] Flow B2C: AI QnA (Knowledge B2C) + Filter + AI Phân tích JSON + Set Topic order + Recall
- [ ] Flow Đặt hàng: AI Tổng quản (JSON, không Chat History) + Python check + If/Recall + API + Xác nhận + Bot API Call Contact list
- [ ] Flow Nhân sự nội bộ: AI Phân tích JSON xác thực + If + AI QnA Knowledge Full
- [ ] Flow Handover: AI Phân tích JSON + Bot API Call ticket
- [ ] Constants: 8 hằng số (Set Const)
- [ ] Filter Bot Reply: 4 regex rules
- [ ] Instruction Prompt B2B: dán đầy đủ (mục 6.3)
- [ ] Instruction Prompt B2C: dán đầy đủ (mục 6.4)

### Giai đoạn 4 – Test & Triển khai
- [ ] Test 12 kịch bản phân luồng (mục 7.2)
- [ ] Test 5 kịch bản Guardrails (mục 7.3)
- [ ] Test end-to-end B2C (8 bước – mục 7.4)
- [ ] Test end-to-end B2B (5 bước – mục 7.4)
- [ ] Test nội bộ (yêu cầu Mã NV)
- [ ] Test 3 SP thiếu giá (missing data)
- [ ] Nạp full 240+ SP vào Knowledge
- [ ] Quick Test lại sau khi nạp full
- [ ] Test regression end-to-end sau khi nạp full
- [ ] Deploy to Production
- [ ] Integration Browser: tạo Profile + kết nối Zalo
- [ ] Integration Browser: tạo Profile + kết nối Facebook (nếu cần)
- [ ] Bàn giao AI CRM: hướng dẫn Dashboard, Manual mode, Q&A, Contact list, Export CSV
- [ ] Bàn giao tài liệu vận hành

---

> **Ghi chú:** Kế hoạch này được xây dựng dựa trên:
> - **TÀI LIỆU YÊU CẦU HUẤN LUYỆN AI AGENT (VHN)** từ sếp – gồm 3 phần: 14 SP thử nghiệm, 5 đề xuất (Persona, Routing Logic, Guardrails, Missing Data, Conversion Goals), sơ đồ phân luồng + lời khuyên thực hiện cuốn chiếu
> - Kiến thức từ khóa học AI Trainer Pro (Buổi 3, 4, 9, 11) trên nền tảng Conductify AI Studio
> - Tài liệu tham khảo: "Conductify Mindflow - AI Agent v1.0" và "Conductify Studio - Knowledge Bank v1.0"
> - Phân tích chi tiết file `[INPUT 2] Sheet thu thập thông tin VHN.xlsx` (12 sheets, 257 SP, 237 Q&A)
