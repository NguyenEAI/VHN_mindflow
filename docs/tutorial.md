# HƯỚNG DẪN TỪNG BƯỚC: HUẤN LUYỆN AI AGENT Y DƯỢC VHN

> **Nền tảng:** Conductify AI Studio
> **Mục tiêu:** Xây dựng AI Sales Agent tư vấn dược mỹ phẩm, phân luồng B2B/B2C, xác thực nhân sự nội bộ
> **Tài liệu tham chiếu:** `requirements.md` (yêu cầu sếp), `ai_sales_agent.txt` (Mindflow mẫu Shegan), `ai.txt` (Mindflow đang xây cho VHN)
> **Chiến lược:** Cuốn chiếu 3 bước theo lời khuyên sếp

---

## MỤC LỤC

- [PHẦN A: CHUẨN BỊ TRƯỚC KHI BẮT ĐẦU](#phần-a-chuẩn-bị-trước-khi-bắt-đầu)
- [BƯỚC CUỐN CHIẾU 1: Company + QnA (Nền tảng kiến thức)](#bước-cuốn-chiếu-1-company--qna)
- [BƯỚC CUỐN CHIẾU 2: Phân luồng B2B/B2C (Router + Sàng lọc)](#bước-cuốn-chiếu-2-phân-luồng-b2bb2c)
- [BƯỚC CUỐN CHIẾU 3: 14 SP thử nghiệm → Full 240+ SP](#bước-cuốn-chiếu-3-14-sp-thử-nghiệm--full-240-sp)
- [PHẦN E: CHECKLIST TỔNG HỢP](#checklist-tổng-hợp)
- [PHẦN F: TRIỂN KHAI & BÀN GIAO](#triển-khai--bàn-giao)

---

## KIẾN TRÚC TỔNG QUAN MINDFLOW (NHÌN MỘT LẦN HIỂU LIỀN)

```
┌────────────────────────────────────────────────────────────┐
│  1. Session Manager  (Extra Fields - khai báo 20+ biến)    │
└────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────┐
│  2. If session.recall_counter > 3  (Safety net chống loop) │
│     → Reset + Bot Send "AI gặp lỗi đường truyền" + Break    │
└────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────┐
│  3. Router  (10 topics: greetings, b2b_consult, b2c_...)   │
└────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────┐
│  4. Flows Switch  (Rẽ nhánh theo topic Router phân)         │
│                                                              │
│   ├─ greetings       → AI QnA + Clear Topic                  │
│   ├─ off_topic       → AI QnA + Clear Topic                  │
│   ├─ company_info    → AI QnA + Clear Topic                  │
│   ├─ brand_info      → AI QnA + Clear Topic                  │
│   ├─ promotion       → AI QnA + Clear Topic                  │
│   ├─ handover        → AI Analyze + API Notify + AI Reply    │
│   ├─ internal_staff  → AI Auth → If authenticated → AI Reply │
│   ├─ b2b_consult     → AI Consult → AI Check Lead → API+Done │
│   ├─ b2c_consult     → AI Consult → AI Check Status → Order  │
│   └─ order           → AI Parse → If full → AI Confirm → API │
└────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────┐
│  5. Filter Bot Reply (TOP-LEVEL, dùng cho TẤT CẢ flow)     │
│     Regex 5: tôi→em, chúng tôi→bên em, bot/AI→tư vấn viên,  │
│              bạn→Anh/Chị, tôi không biết→em chưa có thông    │
└────────────────────────────────────────────────────────────┘
```

> **⚠️ ĐIỂM KHÁC BIỆT QUAN TRỌNG SO VỚI BẢN CŨ:**
> - **Filter Bot Reply** đặt ở **TOP-LEVEL** sau Flows Switch (KHÔNG đặt trong từng flow). Đây là pattern chuẩn từ `ai_sales_agent.txt` của Shegan – chỉ cần khai báo 1 lần, áp dụng cho toàn bộ output.
> - **`saveHumanInput`** thêm vào đầu các flow phức tạp (b2b_consult, b2c_consult, order, internal_staff) để chốt lại input của User trước khi xử lý.
> - **`recall_counter > 3`** là vệ binh chống Recall vô tận khi AI lỗi.
> - **`session.extra.chat_history_b2b` / `chat_history_b2c` / `registration_chat_history`** lưu lịch sử riêng từng luồng để AI parse JSON chính xác hơn.

---

# PHẦN A: CHUẨN BỊ TRƯỚC KHI BẮT ĐẦU

## A.1. Làm sạch dữ liệu trong Excel

Mở file `[INPUT 2] Sheet thu thập thông tin VHN.xlsx`:

### A.1.1. Sửa lỗi tên vendor Floslek

1. Mở sheet **Product**
2. Dùng **Ctrl+H** (Find & Replace)
3. Tìm các vendor name bị lỗi:
   - Find: `\n \t\nFloslek` → Replace: `Floslek`
   - Find: `\nFloslek` → Replace: `Floslek`
4. Kiểm tra: lọc cột vendor → đảm bảo chỉ còn "Floslek" (không có ký tự thừa)

### A.1.2. Xử lý 66 SP thiếu giá

1. Trong sheet **Product**, lọc cột **price** → chọn ô trống
2. Điền giá trị `LIÊN HỆ` vào tất cả ô trống (66 SP)
3. **KHÔNG được bịa giá** – AI sẽ dùng mẫu câu xin SĐT khi gặp "LIÊN HỆ"

### A.1.3. Chuẩn bị file CSV cho QnA

1. Mở sheet **QnA** (237 dòng)
2. Tạo file Excel mới, chỉ giữ **2 cột**: `question` và `answer`
3. Copy 237 cặp Q&A sang file mới
4. **Save As** → chọn **CSV UTF-8 (Comma delimited) (*.csv)**
5. Đặt tên: `vhn_qna.csv`

### A.1.4. Chuẩn bị nội dung cho Knowledge Datasource

Tạo 5 file text (.txt) với nội dung từ Excel:

**File 1: `datasource_company.txt`**
- Copy toàn bộ nội dung từ sheet **Company** (bỏ các dòng "Điền thông tin tại đây")
- Bao gồm: tên công ty, địa chỉ VP HCM + HN, hotline, email, website, lĩnh vực

**File 2: `datasource_brands.txt`**
- Copy từ sheet **Giới thiệu 7 nhãn hàng**
- Bao gồm: Key giới thiệu + Key tư vấn của Christina, Ivatherm, Floslek, Dermoaroma, Preime, Pharmalife

**File 3: `datasource_b2b_products.txt`**
- Lọc sheet **Product**: chỉ lấy SP có `is_salon_product = True` (98 SP)
- Format mỗi SP thành 1 đoạn:
```
---
ID: 1
Tên: Christina - Unstress - Step 1: Gentle Cleansing Milk - 300ml
Vendor: Christina
Giá: 2,398,000 VNĐ
Mô tả: Sữa tẩy trang rửa mặt dành cho da nhạy cảm
Dung tích: 300ml
Loại: B2B (Sản phẩm chuyên nghiệp - is_salon_product = True)
---
```
- Lặp lại cho tất cả 98 SP B2B (giai đoạn đầu nạp 7 SP thử nghiệm: ID 1, 2, 3, 4, 5, 6, 220)
- SP thiếu giá ghi: `Giá: LIÊN HỆ`
- SP thiếu ảnh: KHÔNG ghi trường link_image

**File 4: `datasource_b2c_products.txt`**
- Tương tự File 3, nhưng lọc `is_salon_product = False` (142 SP)
- Format giống nhau, đổi Loại thành: `B2C (Sản phẩm homecare - is_salon_product = False)`
- Giai đoạn đầu nạp 7 SP thử nghiệm: ID 11, 12, 13, 14, 15, 16, 191

**File 5: `datasource_phac_do.txt`**
- Copy từ sheet **Phác đồ Christina** (85 dòng)
- Thêm phần từ sheet **Phác đồ Christina + Máy** (73 dòng)
- Giữ nguyên format gốc

> **Mẹo:** Có thể dùng `extract_data.py` để tự động xuất dữ liệu (đã có sẵn trong working directory).

---

# BƯỚC CUỐN CHIẾU 1: COMPANY + QnA

> **Mục tiêu:** AI có nền tảng kiến thức chung về công ty VHN và câu hỏi thường gặp

## 1.1. Đăng nhập Conductify AI Studio

1. Mở trình duyệt → truy cập **https://conductify.ai/**
2. Đăng nhập bằng tài khoản Admin

## 1.2. Tạo Agent mới

1. Sidebar trái → click **AI Agents**
2. Click nút **"+ Create"**
3. Điền thông tin:

| Trường | Giá trị |
|--------|---------|
| **Name** | `Y Dược VHN Assistant` |
| **Description** | `AI Chuyên viên tư vấn da liễu và chăm sóc khách hàng đại diện cho Công ty Y dược VHN. Hỗ trợ phân luồng B2B (Spa/Clinic/Bệnh viện) và B2C (khách lẻ).` |

4. Click **Create**
5. Agent mới xuất hiện → click vào Agent để mở giao diện **Mindflow**

> **Giao diện Mindflow** gồm 4 khu vực:
> - **Khu vực Mindflow** (trái): kéo thả block
> - **Testing Playground** (phải): test trực tiếp
> - **Block Library** (dưới): thư viện block có sẵn
> - **Agent Profile** (trên): thông tin Agent

## 1.3. Tạo Knowledge Bank – General Knowledge

### 1.3.1. Tạo Book `vhn_general_info`

1. Sidebar trái → click **Knowledges**
2. Tab **General Knowledge** → click **Create new Book**
3. Điền:

| Trường | Giá trị |
|--------|---------|
| **Book Name** | `vhn_general_info` |
| **Access** | Only me |
| **AI Content Analyser** | **VnEm** ← QUAN TRỌNG (vì nội dung tiếng Việt) |

4. Click **Create**

### 1.3.2. Nạp Datasource cho `vhn_general_info`

Vào Book → tab **Datasources** → click **Add new datasource**:

**Datasource 1: `vhn_company`**
- Source format: Text
- Nội dung: paste từ `datasource_company.txt`
- Content Splitter: Paragraph (mặc định)
- → **Save & Process** → đợi xong → **Reload list**

**Datasource 2: `vhn_brands`**
- Source format: Text
- Nội dung: paste từ `datasource_brands.txt`
- → **Save & Process** → **Reload list**

**Datasource 3 (tùy chọn): `vhn_policies`**
- Nội dung: Chính sách bán hàng/vận chuyển/đổi trả
- Nếu VHN chưa cung cấp → bỏ qua, bổ sung sau

### 1.3.3. Kiểm tra datasource

Vào tab **Datasources** → click từng datasource → kiểm tra phần **Text** xem nội dung có đầy đủ không.

## 1.4. Tạo Q&A Library

### 1.4.1. Tạo Library `vhn_qna`

1. Sidebar → **Knowledges** → tab **Questions & Answers**
2. Click **Create new Q&A Library**
3. Điền:

| Trường | Giá trị |
|--------|---------|
| **Q&A Library Name** | `vhn_qna` |
| **Access** | Only me |
| **Language Model** | VnEm (cố định) |

4. Click **Create**

### 1.4.2. Import 237 cặp Q&A từ CSV

1. Trong Q&A Library vừa tạo → click **Import from CSV**
2. Kéo thả file `vhn_qna.csv`
3. Hệ thống hiển thị preview → kiểm tra cột `question` và `answer` khớp
4. Click **Import** → **Confirm** → **Reload list**
5. **Kiểm tra:** Đếm số cặp Q&A = 237

## 1.5. Quick Test Knowledge (BẮT BUỘC)

### 1.5.1. Test Book `vhn_general_info`

1. Vào Book → tab **Quick Test** → Limit = 3
2. Chạy:

| Câu hỏi test | Kỳ vọng kết quả |
|---------------|------------------|
| "Công ty VHN ở đâu?" | Trả về địa chỉ VP HCM + HN |
| "Christina là nhãn hàng gì?" | Trả về Key giới thiệu Christina |
| "VHN phân phối những thương hiệu nào?" | Trả về danh sách 7 nhãn hàng |

3. Nếu kết quả **sai** → sửa datasource → **Save & Process** lại

### 1.5.2. Test Q&A Library `vhn_qna`

| Câu hỏi test | Kỳ vọng kết quả |
|---------------|------------------|
| "Giao hàng bao lâu?" | Trả về Q&A về thời gian giao hàng |
| "Có ship COD không?" | Trả về Q&A về phương thức thanh toán |

## 1.6. Ghi lại UUID (QUAN TRỌNG)

| Loại | Tên | UUID | Ghi chú |
|------|-----|------|---------|
| Book | vhn_general_info | _(paste UUID)_ | Dùng cho Greeting, Off-topic, Company, Brand, Promotion |
| QnA | vhn_qna | _(paste UUID)_ | Dùng cho tất cả flow có AI QnA |

> Trong file `ai.txt` mẫu, các UUID này đang là `137d1103-8486-4047-8951-cc9047a4d9fa` (placeholder cho `vhn_general_info`) và `0c8f748e-c2a3-4e49-81c8-abef5bc014a9` (placeholder cho `vhn_qna`). **Bạn cần thay thế bằng UUID thực tế của mình.**

---

# BƯỚC CUỐN CHIẾU 2: PHÂN LUỒNG B2B/B2C

> **Mục tiêu:** AI nhận diện được khách B2B, B2C, Nội bộ ngay từ câu đầu tiên

## 2.1. Cấu hình Session Manager

1. Quay lại Agent → mở **Mindflow**
2. Click vào block **Session Manager** (block đầu tiên)
3. Tìm mục **Extra Fields** → paste JSON sau:

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
  "employee_authenticated": "no",
  "consultation_stage": "",
  "chat_history_b2b": "",
  "chat_history_b2c": "",
  "registration_chat_history": "",
  "findproduct_chat_history": "",
  "findproduct_data": "",
  "old_order_customer_information": "NA",
  "assistant_role": "Tên của trợ lý là Thảo Vi, Chuyên viên tư vấn da liễu và chăm sóc khách hàng đại diện cho Công ty Y dược VHN.",
  "company_name": "Công ty Cổ phần Xuất Nhập Khẩu & Phân Phối Sản Phẩm Y Dược VHN",
  "company_short_name": "Y dược VHN",
  "company_contact": "Hotline: 0941905885",
  "product_main_keyword": "Dược mỹ phẩm quốc tế & giải pháp da liễu thẩm mỹ",
  "company_product": "Christina (Unstress, Bio Phyto, Comodex...), Ivatherm, Floslek, Dermoaroma, Preime, Pharmalife - các dòng dược mỹ phẩm chuyên nghiệp và homecare"
}
```

> **Mẹo:** JSON Extra Fields đầy đủ (kèm `assistant_skill`, `assistant_scope`, `assistant_tone`, `vn_pronoun`, `register_successfully`, `stop_examples`, `required_fields_for_b2c_order`, `required_fields_for_b2b_lead`) đã có sẵn trong file `ai.txt` (block đầu tiên - `Session Manager`). Copy nguyên từ đó vào.

4. **Save**

### Giải thích các biến mới (so với bản cũ)

| Biến | Mục đích |
|------|----------|
| `employee_authenticated` | "yes"/"no" – lưu trạng thái xác thực để các luồng sau biết NV đã được xác thực chưa, không bắt khai báo lại |
| `registration_chat_history` | Buffer lịch sử khi User đang trong luồng đặt hàng (giúp AI parse JSON chính xác hơn so với dùng chat_history gốc) |
| `findproduct_chat_history` | Buffer lịch sử tư vấn sản phẩm |
| `findproduct_data` | Lưu tên sản phẩm User đang quan tâm (để khi User chốt đơn nói "lấy em cái đó", AI biết "cái đó" là gì) |
| `old_order_customer_information` | Lưu Họ tên/SĐT/Địa chỉ đơn cũ. Khi User đặt đơn mới, AI sẽ hỏi: "Anh/Chị muốn dùng thông tin cũ hay nhập mới?" |
| `chat_history_b2b` / `chat_history_b2c` | Buffer riêng cho từng luồng tư vấn, để AI tổng hợp lead/order chính xác |

### Kiểm tra Session Manager

1. Bật **Show Raw Output** ở Testing Playground
2. Nhắn thử: "Xin chào"
3. Xem Raw Output → kiểm tra các biến session có hiển thị không

## 2.2. ⚠️ THÊM MỚI: Safety Net "If session.recall_counter > 3"

> **Tại sao cần?** Khi AI parse JSON sai hoặc gặp lỗi network, các block `Recall` có thể chạy lặp vô tận, đốt cháy quota. Pattern này từ `ai_sales_agent.txt` (block thứ 3 trong sequence).

Sau Session Manager, **trước Router**, thêm 1 block **If**:

| Trường | Giá trị |
|--------|---------|
| **Condition** | `session.recall_counter > 3` |

Trong nhánh **True** → kéo thả tuần tự:

1. **Set Var**: `varName = session.recall_counter`, `varValue = 0`
2. **Set Var**: `varName = topic`, `varValue = json.dumps(session)` (để clear topic hiện tại)
3. **Bot Send Text**: `"Dạ, em vừa gặp chút vấn đề với đường truyền. Anh/Chị vui lòng gửi lại thông tin vừa rồi giúp em nhé ạ."`
4. **Break** ← block kết thúc Mindflow turn này

Nhánh **False** → để trống (chạy tiếp xuống Router).

## 2.3. Cấu hình Router

1. Click vào block **Router** trong Mindflow
2. Thêm 10 topic bằng nút **Add topic**

> **Cách thêm Phrases:** Trong ô Phrases, gõ từng câu và nhấn Enter sau mỗi câu.

### Topic 1: `greetings`
```
hello
hi
chào
xin chào
em ơi
có ai không
Tôi cần hỗ trợ
hỗ trợ tôi với
Tôi muốn hỏi về vấn đề sau
chào shop
alo
shop ơi
```

### Topic 2: `off_topic`
```
làm thơ
viết code
write poetry
write code
kể chuyện hài
Assistant là một Sales Agent. Vì vậy off_topic khi User nói nhảm, tán tỉnh, nói những chủ đề không liên quan tới tìm và tư vấn sản phẩm, mua hàng
Khi User nhắn chuỗi các ký tự đặc biệt ##&$%%^%$*%*O^(√ (*&^*$%#$
Khi User gửi duy nhất 1 số "9"
9
```

### Topic 3: `company_info`
```
công ty VHN ở đâu
địa chỉ cửa hàng
số hotline bao nhiêu
giờ làm việc của công ty
liên hệ VHN qua đâu
email công ty là gì
văn phòng ở Hà Nội chỗ nào
chính sách đổi trả
chính sách bảo mật
chính sách vận chuyển
điều khoản và dịch vụ
đổi hàng
trả hàng
```

### Topic 4: `brand_info`
```
Christina là nhãn hàng gì
giới thiệu về Ivatherm
Floslek có những dòng sản phẩm nào
Dermoaroma là thương hiệu nước nào
Preime có tốt không
Pharmalife bán gì
các nhãn hàng VHN phân phối
thương hiệu nào tốt nhất
Christina của nước nào
Ivatherm xuất xứ ở đâu
```

### Topic 5: `b2b_consult`
```
mình muốn mua sỉ cho spa
tôi cần sản phẩm cho thẩm mỹ viện
bảng giá đại lý bao nhiêu
chiết khấu cho đại lý là bao nhiêu
spa muốn nhập hàng
sản phẩm cho bệnh viện da liễu
tôi là chủ nhà thuốc muốn tìm hiểu
step trị liệu chuyên nghiệp
phác đồ điều trị da mụn cho spa
sản phẩm chuyên dùng trong phòng khám
sản phẩm cho clinic
mua sỉ sản phẩm Christina
Step 1
Step 2
Step 3 Probiotic Peel
Frangipani Concentrate
Total Serenity Serum 100ml
Relaxing Massage Cream
Skin Renew
mở spa
kinh doanh spa
muốn làm đại lý
```

> **Dấu hiệu B2B (theo sếp):** Khách nhắc Spa, Thẩm mỹ viện, Clinic, Bệnh viện, Nhà thuốc, Đại lý; hỏi chiết khấu, mua sỉ, bảng giá đại lý, Step 1-10. Đã bổ sung tên các SP B2B tiêu biểu để Router phân chính xác hơn.

### Topic 6: `b2c_consult`
```
da mình bị mụn tư vấn giúp
kem dưỡng da nào tốt
mình da nhạy cảm dùng gì
routine chăm sóc da buổi tối
mình muốn mua kem chống nắng
sản phẩm trị nám cho da
tư vấn sản phẩm cho da dầu
mình muốn mua sản phẩm dùng tại nhà
mua lẻ sản phẩm được không
da mình bị lão hóa dùng gì
tư vấn routine chăm sóc da tại nhà
Gentle Cleansing Milk 300ml
Stabilizing Toner
Total Serenity Serum 50ml
Probiotic Day Cream SPF 15
Harmonizing Night Cream
Replenishing Mask
Cicaderm Cream
da khô dùng gì
da hỗn hợp
kem dưỡng ẩm
kem ban đêm
mặt nạ dưỡng
tẩy trang mặt
sữa rửa mặt cho da nhạy cảm
```

> **Dấu hiệu B2C:** Khách hỏi mua lẻ, mô tả tình trạng da cá nhân, cần tư vấn routine tại nhà. Đã bổ sung tên SP B2C tiêu biểu.

### Topic 7: `order`
```
mình muốn đặt hàng
chốt đơn giúp mình
mình lấy sản phẩm đó
mua luôn
thêm vào giỏ hàng
thanh toán như nào
giao hàng về đâu
đặt hàng
cho anh order
lấy anh sản phẩm này
ok lấy anh món đó
cho anh đăng ký
```

### Topic 8: `internal_staff`
```
tôi là nhân viên công ty
liệt kê sản phẩm key của dòng Unstress
báo cáo số lượng sản phẩm
thông tin nội bộ
danh sách sản phẩm theo vendor
mã nhân viên của tôi là
tôi thuộc phòng
phòng Sales
phòng Marketing
phòng Kinh doanh
key product
key của dòng
thống kê sản phẩm
doanh thu
tồn kho nội bộ
```

> **Theo sếp:** AI phải yêu cầu **Bộ phận + Mã số nhân viên** trước khi trả lời thông tin nội bộ.

### Topic 9: `handover`
```
i want to talk to someone
talk to a human
transfer me to a representative
I would like to speak to a human
i don't want to talk to the bot anymore
Tôi muốn nói chuyện với ai đó
Chuyển tôi đến gặp nhân viên
Tôi muốn gặp quản lý
Kết nối tôi với nhân viên
cho mình gặp quản lý
tôi muốn khiếu nại
không hài lòng với sản phẩm
gọi nhân viên hỗ trợ
cần nói chuyện với người thật
yêu cầu hỗ trợ trực tiếp
tra cứu trạng thái đơn hàng
đơn hàng giao tới đâu rồi
complain
check vị trí giao hàng
check hạn sử dụng
```

### Topic 10: `promotion`
```
có khuyến mãi gì không
chương trình giảm giá
voucher ưu đãi
mua 1 tặng 1 không
đang có sale gì không
có giảm giá không
mua nhiều có giảm không
có tặng kèm không
```

> **3 QUY TẮC TUYỆT ĐỐI khi cấu hình Phrases:**
> 1. Ưu tiên dùng Phrases (câu tự nhiên), hạn chế Keywords
> 2. Tên topic viết liền, không dấu, không khoảng trắng
> 3. Mỗi topic nên có ≥ 5-10 phrases để Router phân chính xác

## 2.4. Cấu hình Flows Switch

1. Click vào block **Flows Switch** trong Mindflow
2. Tạo 10 flow bằng nút **Add Flow**

| # | Flow name | Topic gán |
|---|-----------|-----------|
| 1 | `greetings` | greetings |
| 2 | `off_topic` | off_topic |
| 3 | `company_info` | company_info |
| 4 | `brand_info` | brand_info |
| 5 | `b2b_consult` | b2b_consult |
| 6 | `b2c_consult` | b2c_consult |
| 7 | `order` | order |
| 8 | `internal_staff` | internal_staff |
| 9 | `handover` | handover |
| 10 | `promotion` | promotion |

> **3 QUY TẮC TUYỆT ĐỐI:**
> 1. Mỗi flow gán đúng **1 topic** (không gán nhiều topic cho 1 flow)
> 2. **TUYỆT ĐỐI** không nhập topic không có ở Router
> 3. **TUYỆT ĐỐI** không để trống Topics trong bất kỳ flow nào

## 2.5. Xây dựng Flow Chào hỏi (`greetings`)

Click vào flow `greetings` → kéo thả block:

### Block 1: AI QnA

| Trường | Giá trị |
|--------|---------|
| **Name** | `AI_Greeting` |
| **Knowledge Dataset UUID** | _(UUID của Book `vhn_general_info`)_ |
| **Knowledge Dataset QA UUID** | _(UUID của Library `vhn_qna`)_ |
| **Enable Knowledge Aware** | ✅ ON |
| **Enable Chat History Aware** | ✅ ON |
| **Enable Human Input Aware** | ✅ ON |
| **Variable to save AI reply** | `bot_reply` |
| **Knowledge Result Limit** | `2` |
| **Temperature** | `0.7` |
| **Max Tokens** | `1000` |
| **AI Model** | `gpt-4o-mini` |

**Instruction Prompt:** _(đã có trong `ai.txt` block `cdb1ad21c83bc74313ca4db70dd9090a`)_

```
# Vai trò
Bạn là Thảo Vi, Chuyên viên tư vấn da liễu và chăm sóc khách hàng đại diện cho Công ty Y dược VHN.

# Giọng điệu
Chuyên nghiệp, lịch sự, chuẩn y khoa, tận tâm và đáng tin cậy.

# Nhiệm vụ
- Chào hỏi khách, giới thiệu mình là Thảo Vi.
- Cho User biết em có thể: (1) Tư vấn dược mỹ phẩm chuyên nghiệp cho Spa/Clinic (B2B), (2) Tư vấn sản phẩm homecare (B2C), (3) Thông tin về VHN và 7 nhãn hàng.
- Hỏi khéo: "Dạ, không biết Anh/Chị đang cần tìm sản phẩm để chăm sóc da tại nhà hay dùng cho dịch vụ tại Spa/phòng khám ạ?" để sàng lọc B2B/B2C.

# Quy tắc
- Trả lời dưới 80 từ.
- KHÔNG xưng "tôi", "mình". Xưng "em", gọi khách "Anh/Chị".
- KHÔNG được nói mình là "chatbot", "bot", "AI". Luôn nói mình là "chuyên viên tư vấn".
```

### Block 2: Clear Topic

Kéo block **Clear Topic** vào cuối flow.

> **⚠️ KHÔNG đặt Filter Bot Reply ở đây.** Filter sẽ được đặt ở TOP-LEVEL (sau Flows Switch).

**Kết quả flow Chào hỏi:**
```
[AI QnA] → [Clear Topic]
```

## 2.6. Xây dựng Flow Off-topic (`off_topic`)

| Block | Cấu hình |
|-------|----------|
| **AI QnA** | Instruction: từ chối khéo, hướng lại chủ đề chính. Dataset UUID: vhn_general_info + vhn_qna. Dưới 30 từ. |
| **Clear Topic** | Xóa topic |

Instruction prompt đã có trong `ai.txt` block `bfa4ac4f47b3f23d5ee18a7a140f9e3f`.

## 2.7. Xây dựng Flow Thông tin chung (`company_info`)

| Block | Cấu hình |
|-------|----------|
| **AI QnA** | Instruction: trả lời về VHN dựa Knowledge. Dataset UUID: vhn_general_info + vhn_qna. Bao gồm chính sách bảo mật, đổi trả, vận chuyển. Dưới 100 từ. |
| **Clear Topic** | Xóa topic |

## 2.8. Xây dựng Flow Giới thiệu nhãn hàng (`brand_info`)

| Block | Cấu hình |
|-------|----------|
| **AI QnA** | Instruction: giới thiệu 6-7 nhãn. Nếu User hỏi nhãn cụ thể → Key giới thiệu + Key tư vấn. Christina nhấn mạnh "phân phối tại 2000+ Bệnh viện/Spa toàn cầu". Dưới 80 từ. |
| **Clear Topic** | Xóa topic |

## 2.9. Xây dựng Flow Khuyến mãi (`promotion`)

| Block | Cấu hình |
|-------|----------|
| **AI QnA** | Instruction: từ chối giảm thêm, chỉ có ưu đãi combo. Chỉ nhận COD, không nhận chuyển khoản/voucher. Xin SĐT nếu User muốn cập nhật ưu đãi. Dưới 60 từ. |
| **Clear Topic** | Xóa topic |

## 2.10. Xây dựng Flow Handover (`handover`) – ⚠️ NÂNG CẤP

Flow này được nâng cấp theo pattern từ `ai_sales_agent.txt` (block `6c0a0d6f4c565b883e2911dfe40fe6ef`):

### Block 1: AI QnA – Phân tích lý do

| Trường | Giá trị |
|--------|---------|
| **Enable JSON Mode** | ✅ ON |
| **Variable to save** | `handover_analyze` |
| **Temperature** | `0.3` |

**Instruction:**
```
You are a helpful Assistant that only responds in JSON with "reason" variable.

Read chat history và phân tích User vừa yêu cầu gì? Lý do muốn gặp quản lý?

Format: {"reason": "..."}
- Trả lời ngắn gọn nhất có thể
- Biến "reason" giữ tiếng Anh (để API nội bộ đọc được)
```

### Block 2: Set Var
| Variable | Expression |
|----------|------------|
| `handover` | `json.loads("{{handover_analyze}}")` |

### Block 3: Bot API Call – Notify Staff
| Trường | Giá trị |
|--------|---------|
| **API URL** | `https://api.workerbot.ai/v1/handover/notify` |
| **Method** | POST |
| **Body** | (xem trong `ai.txt` block `h3c4d5e6...`) |

### Block 4: AI QnA – Reply User

Trả lời User: xin lỗi, đã chuyển yêu cầu cho chuyên viên, sẽ liên hệ trong vài phút. Nếu User gửi ngày giờ cụ thể, hỏi xem có muốn đặt lịch không.

### Block 5: Clear Topic

## 2.11. TEST PHÂN LUỒNG (Bước 2 cuốn chiếu)

Đây là bước quan trọng! Test bằng câu mẫu sếp yêu cầu:

1. Mở **Testing Playground**
2. Bật **Show Raw Output**
3. Chạy từng câu:

| # | Câu test | Kỳ vọng Topic | Kỳ vọng Flow |
|---|----------|----------------|--------------|
| 1 | "Xin chào" | greetings | Chào hỏi |
| 2 | "Mình muốn mua sỉ cho spa" | b2b_consult | Tư vấn B2B |
| 3 | "Da mình nhạy cảm lắm, tư vấn giúp mình" | b2c_consult | Tư vấn B2C |
| 4 | "Liệt kê các sản phẩm key của dòng Unstress" | internal_staff | Nội bộ |
| 5 | "Công ty VHN ở đâu?" | company_info | Thông tin chung |
| 6 | "Tôi muốn mua sản phẩm cho bệnh viện" | b2b_consult | Tư vấn B2B |
| 7 | "Mình muốn mua kem dưỡng đêm để dùng" | b2c_consult | Tư vấn B2C |
| 8 | "Bảng giá đại lý bao nhiêu?" | b2b_consult | Tư vấn B2B |
| 9 | "Cho mình gặp quản lý" | handover | Gọi hỗ trợ |
| 10 | "Christina là nhãn hàng gì?" | brand_info | Nhãn hàng |

**Cách kiểm tra Raw Output:**
- Xem **Router** phân đúng topic chưa?
- Xem **Flows Switch** kích hoạt đúng flow chưa?
- Xem AI QnA response có chính xác không?

> Nếu Router phân sai → quay lại chỉnh **Phrases** cho topic tương ứng.

---

# BƯỚC CUỐN CHIẾU 3: 14 SP THỬ NGHIỆM → FULL 240+ SP

> **Mục tiêu:** AI đề xuất đúng SP cho đúng đối tượng, test với 14 SP trước khi nạp full

## 3.1. Tạo thêm Knowledge Book cho B2B và B2C

### 3.1.1. Tạo Book `vhn_b2b_product`

1. Sidebar → **Knowledges** → **General Knowledge** → **Create new Book**
2. Điền:

| Trường | Giá trị |
|--------|---------|
| **Book Name** | `vhn_b2b_product` |
| **Access** | Only me |
| **AI Content Analyser** | **VnEm** |

3. Tab **Datasources** → thêm:

**Datasource 1: `b2b_products`**
- Source format: Text
- **Giai đoạn đầu:** Chỉ nạp 7 SP B2B thử nghiệm (ID 1, 2, 3, 4, 5, 6, 220) từ `datasource_b2b_products.txt`
- → Save & Process

**Datasource 2: `phac_do_christina`**
- Source format: Text
- Nội dung: paste từ sheet **Phác đồ Christina** (85 dòng)
- → Save & Process

**Datasource 3: `phac_do_christina_may`**
- Source format: Text
- Nội dung: paste từ sheet **Phác đồ Christina + Máy** (73 dòng)
- → Save & Process

### 3.1.2. Tạo Book `vhn_b2c_product`

| Trường | Giá trị |
|--------|---------|
| **Book Name** | `vhn_b2c_product` |
| **Access** | Only me |
| **AI Content Analyser** | **VnEm** |

Datasource: `b2c_products`
- Nội dung: 7 SP B2C thử nghiệm (ID 11, 12, 13, 14, 15, 16, 191)
- → Save & Process

### 3.1.3. Quick Test Book B2B & B2C

| Test trên | Câu hỏi | Kỳ vọng |
|-----------|---------|---------|
| `vhn_b2b_product` | "Sản phẩm trị liệu bước 3" | Trả về Step 3 Probiotic Peel (ID 3) |
| `vhn_b2b_product` | "Phác đồ Unstress" | Trả về phác đồ Unstress |
| `vhn_b2c_product` | "Kem dưỡng da ban đêm" | Trả về Harmonizing Night Cream (ID 15) |
| `vhn_b2c_product` | "Kem chống nắng" | Trả về Probiotic Day Cream SPF 15 (ID 14) |

### 3.1.4. Cập nhật bảng UUID

| Loại | Tên | UUID | Dùng cho Flow |
|------|-----|------|---------------|
| Book | vhn_general_info | _(đã có)_ | greetings, off_topic, company_info, brand_info, promotion |
| Book | vhn_b2b_product | _(paste mới)_ | b2b_consult, internal_staff |
| Book | vhn_b2c_product | _(paste mới)_ | b2c_consult, order |
| QnA | vhn_qna | _(đã có)_ | Tất cả flow có AI QnA |

> Trong `ai.txt`, các UUID placeholder hiện tại:
> - `vhn_b2b_product`: `753ca5a0-738a-47a1-8cea-b50ea63a925c`
> - `vhn_b2c_product`: `550cb442-e727-4086-b0a9-9da2f5ec1a70`
> - Bạn cần thay thế bằng UUID thực tế của mình.

## 3.2. Xây dựng Flow Tư vấn B2B (`b2b_consult`) – ⚠️ NÂNG CẤP

Flow B2B được nâng cấp với 6 block theo pattern Shegan:

```
[Save human_input] → [AI Chuyên trách B2B] → [Save chat_history_b2b] → [Save session]
→ [AI Phân tích thu thập info] → [Set b2b_info] → [Parallel: YES/NO/EXIT]
```

### Block 1: Save Human Input

| Trường | Giá trị |
|--------|---------|
| **Type** | `saveHumanInput` |
| **Human Input** | `{human_input}` |

> **Tại sao cần?** Pattern Shegan: lưu lại input trước khi xử lý để các block sau dùng tham chiếu cố định (`{{ human_input }}`) thay vì giá trị dao động.

### Block 2: AI QnA Chuyên trách B2B

| Trường | Giá trị |
|--------|---------|
| **Name** | `AI_B2B_Consultant` |
| **Knowledge Dataset UUID** | _(UUID của Book `vhn_b2b_product`)_ |
| **Knowledge Dataset QA UUID** | _(UUID của Library `vhn_qna`)_ |
| **Enable Knowledge Aware** | ✅ ON |
| **Enable Chat History Aware** | ✅ ON |
| **Enable Human Input Aware** | ✅ ON |
| **Variable to save** | `bot_b2b_reply` |
| **Result Limit** | `3` |
| **Temperature** | `0.7` |
| **Max Tokens** | `1500` |
| **AI Model** | `gpt-4o-mini` |

**Instruction Prompt** (đã có đầy đủ trong `ai.txt` block `ab857731942256b92e4b2adc4c708cb8`). Tóm tắt:

```
# Vai trò
{{ session.extra.assistant_role }}

# Đối tượng
Khách hàng B2B: Spa, Thẩm mỹ viện, Clinic, Bệnh viện, Nhà thuốc, Đại lý.

# Quy trình (linh hoạt)
1. Hỏi tên
2. Hỏi tên cơ sở + khu vực
3. Hỏi dịch vụ chính
4. Hỏi thiết bị công nghệ cao
5. Đề xuất SP B2B (is_salon_product = True)
6. Nhấn mạnh uy tín Christina (2000+ Spa toàn cầu)
7. Khi User hỏi chiết khấu/giá sỉ → từ chối, xin Tên+SĐT+Cơ sở+Địa chỉ
8. Thu thập đủ → chuyển Sales

# Guardrails NGHIÊM NGẶT
- CHỈ giới thiệu SP is_salon_product = True
- KHÔNG bịa giá sỉ, chiết khấu
- KHÔNG tiết lộ thông tin nội bộ
- SP thiếu giá → mẫu câu "ưu đãi đặc biệt, để lại SĐT"
- KHÔNG nói mình là chatbot/AI
```

### Block 3: Python – Save chat_history_b2b

```python
output = '''{{session.extra.chat_history_b2b}}'''
output = output + "Customer: " + '''{{human_input}}''' + "   \n   "
output = output + "Supporter: " + '''{{bot_b2b_reply}}''' + "   \n   "
print(output)
```

Variable name: `session.extra.chat_history_b2b`

### Block 4: Session Save

Kéo block **Session Save** (không cần config).

### Block 5: AI QnA – Phân tích thu thập info

| Trường | Giá trị |
|--------|---------|
| **Enable JSON Mode** | ✅ ON |
| **Enable Chat History Aware** | ✅ ON |
| **Variable to save** | `ai_b2b_check` |
| **Temperature** | `0.3` |

**Instruction:**
```
Phân tích chat history B2B để kiểm tra User đã cung cấp đủ thông tin liên hệ chưa.

Chat history:
"""
{{ session.extra.chat_history_b2b }}
Customer: {{ human_input }}
"""

Trả lời JSON:
- Đủ: {"status": "YES", "name": "...", "phone": "...", "facility": "...", "address": "..."}
- Chưa đủ: {"status": "NO"}
- Muốn thoát: {"status": "EXIT"}

Rules:
- SĐT phải 10-11 số
- Địa chỉ phải có quận/huyện + tỉnh/thành
- Tên cơ sở rõ ràng
- JSON only, no markdown
```

### Block 6: Set Var
| Variable | Expression |
|----------|------------|
| `b2b_info` | `json.loads("{{ai_b2b_check}}")` |

### Block 7: Parallel (3 nhánh)

**Nhánh conditionA:** `b2b_info.status == "YES"`
1. **Bot API Call** – Ghi nhận Lead B2B
   - URL: `https://api.workerbot.ai/v1/contact-list/create`
   - Body: `{name, phone, address, company: facility, full_field: {type: "B2B_LEAD"}}`
2. **Bot Send Text**: "Dạ, em đã ghi nhận thông tin... Chuyên viên kinh doanh sẽ liên hệ..."
3. **Set Var**: `session.extra.chat_history_b2b = empty_str()` (clear buffer)
4. **Session Save**
5. **Clear Topic**

**Nhánh conditionB:** `b2b_info.status == "NO"`
- **Bot Send Text**: `{{ bot_b2b_reply }}` (gửi reply AI đã tạo)

**Nhánh conditionC:** `b2b_info.status == "EXIT"`
- **Bot Send Text** cảm ơn
- **Clear Topic**

## 3.3. Xây dựng Flow Tư vấn B2C (`b2c_consult`) – ⚠️ NÂNG CẤP

Pattern tương tự B2B nhưng có thêm extract product để nuôi luồng `order`:

```
[Save human_input] → [AI Chuyên trách B2C] → [Save chat_history_b2c]
→ [AI Extract Product of Interest] → [Save findproduct_data] → [Save session]
→ [AI Check Status: READY/CONTINUE/EXIT] → [Set b2c_status] → [Parallel]
```

### Block 1: Save Human Input
| Trường | Giá trị |
|--------|---------|
| **Human Input** | `{human_input}` |

### Block 2: AI QnA Chuyên trách B2C

| Trường | Giá trị |
|--------|---------|
| **Name** | `AI_B2C_Consultant` |
| **Knowledge Dataset UUID** | _(UUID của Book `vhn_b2c_product`)_ |
| **Knowledge Dataset QA UUID** | _(UUID của Library `vhn_qna`)_ |
| **Variable to save** | `bot_b2c_reply` |
| **Result Limit** | `3` |
| **Temperature** | `0.7` |

**Instruction:** (đã có trong `ai.txt` block `8a045fd50c088e3adf5f000f40c21d66`)

Tóm tắt quy trình 10 bước + Guardrails:
- CHỈ đề xuất SP homecare (is_salon_product = False)
- TUYỆT ĐỐI KHÔNG đề xuất SP B2B (Step trị liệu) cho khách B2C → tránh kích ứng
- Nếu User hỏi SP B2B (vd "Cho em mua Step 3 Probiotic Peel") → từ chối + gợi ý SP homecare tương đương
- SP thiếu giá → mẫu câu "ưu đãi đặc biệt, để lại SĐT"
- Nếu User có thai/cho con bú → cảnh báo cẩn trọng

### Block 3: Python – Save chat_history_b2c

```python
output = '''{{session.extra.chat_history_b2c}}'''
output = output + "Customer: " + '''{{human_input}}''' + "   \n   "
output = output + "Supporter: " + '''{{bot_b2c_reply}}''' + "   \n   "
print(output)
```

Variable: `session.extra.chat_history_b2c`

### Block 4: AI QnA – Extract Product of Interest ⚠️ MỚI

| Trường | Giá trị |
|--------|---------|
| **Enable JSON Mode** | ❌ OFF |
| **Enable Chat History Aware** | ❌ OFF (chỉ đọc chat_history_b2c trong instruction) |
| **Variable to save** | `extracted_product` |
| **Temperature** | `0.3` |

**Instruction:**
```
# Task
Phân tích Customer-Supporter conversation trong triple quotes để trích xuất "Sản phẩm mà Customer từng hỏi đến / Supporter đã gợi ý".

""" {{ session.extra.chat_history_b2c }} """

Customer có thể không nói rõ ràng ("cho em cái đó", "ok", "em lấy"). Assistant phải nhận diện thông minh.

# Constraint
- Chỉ trả lời tên SP đầy đủ, ngắn gọn (1-3 SP)
- Nếu không xác định → "NA"
```

> **Tại sao block này?** Khi User nói "Em lấy cái đó nha", flow `order` sẽ đọc `session.extra.findproduct_data` để biết "cái đó" là gì → parse JSON `product_requirement` chính xác.

### Block 5: Set Var
| Variable | Expression |
|----------|------------|
| `session.extra.findproduct_data` | `extracted_product` |

### Block 6: Session Save

### Block 7: AI QnA – Check B2C Status

| Trường | Giá trị |
|--------|---------|
| **Enable JSON Mode** | ✅ ON |
| **Variable to save** | `ai_b2c_check` |
| **Temperature** | `0.3` |

**Instruction:**
```
Phân tích cuộc hội thoại, User đã sẵn sàng đặt hàng chưa?

- "READY": Muốn đặt hàng, chốt đơn
- "CONTINUE": Đang tìm hiểu, cần tư vấn thêm
- "EXIT": Muốn kết thúc / hủy / chuyển chủ đề

Trả lời JSON: {"status": "READY|CONTINUE|EXIT"}
```

### Block 8: Set Var
| Variable | Expression |
|----------|------------|
| `b2c_status` | `json.loads("{{ai_b2c_check}}")` |

### Block 9: Parallel (3 nhánh)

**Nhánh ready:** `b2c_status.status == "READY"`
1. **Set Topic**: `order`
2. **Recall** (max_loop=10) → chuyển sang flow order

**Nhánh continue:** `b2c_status.status == "CONTINUE"`
- **Bot Send Text**: `{{ bot_b2c_reply }}` (gửi reply AI đã tạo)

**Nhánh exit:** `b2c_status.status == "EXIT"`
- **Bot Send Text** cảm ơn
- **Clear Topic**

> **⚠️ CẢNH BÁO:** KHÔNG đặt block **Clear Topic** ở nhánh ready. Vì sau Recall, topic mới (`order`) cần được giữ để Router/Flows Switch chạy đúng.

## 3.4. Xây dựng Flow Đặt hàng (`order`) – ⚠️ NÂNG CẤP HOÀN TOÀN

Đây là flow phức tạp nhất, theo pattern Shegan `place_order`:

```
[Save human_input] → [AI Parse Order JSON] → [Set order_info]
→ [If exit? → Cleanup + Clear]
→ [Python check completeness: YES/NO]
   ├─ NO  → [AI Ask Missing] → [Save reg_history] → [Save session] → [Bot Send]
   └─ YES → [AI Check Confirmation: yes/no/exit]
            ├─ yes  → [API Call] → [Success msg] → [Save old_order] → [Cleanup] → [Clear Topic]
            └─ no   → [Recall] (chờ User xác nhận)
```

### Block 1: Save Human Input

### Block 2: AI Parse Order JSON

| Trường | Giá trị |
|--------|---------|
| **Enable JSON Mode** | ✅ ON |
| **Enable Chat History Aware** | ❌ OFF |
| **Variable to save** | `ai_order_parse` |
| **Temperature** | `0.3` |

**Instruction:** (đã có trong `ai.txt` block `307845791d26a06afa12b673d8c04f62`)

Đọc:
- `{{ session.extra.findproduct_data }}` (SP User quan tâm)
- `{{ session.extra.old_order_customer_information }}` (info đơn cũ)
- `{{ session.extra.registration_chat_history }}` (chat buffer)
- `{{ human_input }}` (input mới)

Output JSON:
```json
{
  "product_requirement": "tên SP + số lượng",
  "customer_name": "họ tên",
  "customer_phone": "số ĐT",
  "customer_address": "địa chỉ đầy đủ",
  "is_customer_want_to_exit": "yes|no"
}
```

Rules:
- Field thiếu → `"NOT-PROVIDED"`
- SĐT sai format → `"NOT-PROVIDED"`
- Địa chỉ thiếu quận/tỉnh → `"NOT-PROVIDED"`

### Block 3: Set Var
| Variable | Expression |
|----------|------------|
| `order_info` | `json.loads("{{ai_order_parse}}")` |

### Block 4: If exit?

Condition: `order_info.is_customer_want_to_exit == "yes"`

**True:**
1. **Bot Send Text**: "Dạ, em đã tạm dừng đặt hàng. Khi nào cần em tư vấn tiếp, cứ nhắn em nhé ạ."
2. **Set Var**: `session.extra.registration_chat_history = empty_str()`
3. **Session Save**
4. **Clear Topic**

**False:** (bỏ trống – tiếp tục xuống Block 5)

### Block 5: Python – Check Completeness

```python
import json
order = json.loads('{{ai_order_parse}}')
required = ['product_requirement', 'customer_name', 'customer_phone', 'customer_address']
missing = [f for f in required if order.get(f, 'NOT-PROVIDED') == 'NOT-PROVIDED' or not order.get(f)]
if not missing:
    print('YES')
else:
    print('NO')
```

Variable: `order_check`

### Block 6: If order_check == NO

**True (NO – chưa đủ thông tin):**

1. **AI QnA – Ask Missing Info**

   | Trường | Giá trị |
   |--------|---------|
   | **Knowledge Dataset UUID** | _(UUID của Book `vhn_b2c_product`)_ |
   | **Variable to save** | `bot_reply` |
   | **Temperature** | `0.5` |

   **Instruction:**
   ```
   # Context
   Thông tin đã thu thập: {{ ai_order_parse }}

   # Task
   User muốn đặt hàng nhưng còn thiếu thông tin. Khéo léo hỏi field còn NOT-PROVIDED:
   - Họ tên
   - SĐT (10-11 số)
   - Địa chỉ đầy đủ (số nhà + đường + quận/huyện + tỉnh/thành)
   - Sản phẩm + số lượng

   Rules:
   - KHÔNG hỏi lại field đã có
   - Tối đa 2 field/lần, KHÔNG dồn
   - Khi đủ → TỔNG HỢP bullet point + "Anh/Chị xác nhận đơn hàng giúp em không ạ?"

   # Constraint
   - Dưới 100 từ
   - KHÔNG bịa giá
   - Chỉ nhận COD
   ```

2. **Python – Collect Register Chat History**
   ```python
   output = '''{{session.extra.registration_chat_history}}'''
   output = output + "Customer: " + '''{{human_input}}''' + "   \n   "
   output = output + "Supporter: " + '''{{bot_reply}}''' + "   \n   "
   print(output)
   ```
   Variable: `session.extra.registration_chat_history`

3. **Session Save**

4. **Bot Send Text**: `{{ bot_reply }}`

**False (YES – đã đủ thông tin):**

1. **AI QnA – Check Confirmation**

   | Trường | Giá trị |
   |--------|---------|
   | **Enable JSON Mode** | ✅ ON |
   | **Variable to save** | `ai_confirm_check` |
   | **Temperature** | `0.3` |

   **Instruction:**
   ```
   Assistant strictly reviews chat history để extract confirmation.

   # Conversation
   """ {{ session.extra.registration_chat_history }}
   Customer: {{ human_input }}
   """

   # Task
   - Step 1: Verify Họ tên + SĐT + Địa chỉ + Sản phẩm đã có
   - Step 2: Assistant đã tổng hợp đơn cho User xem chưa?
   - Step 3: User đã XÁC NHẬN ("ok", "đúng rồi", "chốt"...) chưa?

   # Response
   - Cả 3 OK: {"decision": "yes", "reason": "..."}
   - Chưa: {"decision": "no", "reason": "..."}
   - Hủy: {"decision": "exit", "reason": "..."}

   JSON only.
   ```

2. **Set Var**: `confirm_info = json.loads("{{ai_confirm_check}}")`

3. **If `confirm_info.decision == "yes"`:**

   **True:**
   - **Bot API Call** – Ghi nhận đơn
     - URL: `https://api.workerbot.ai/v1/contact-list/create`
     - Body: `{name, phone, address, product_requirement, full_field: {type: "B2C_ORDER"}}`
   - **Bot Send Text** – Confirmation:
     ```
     Dạ, em đã ghi nhận đơn hàng:
     - Họ tên: {{order_info.customer_name}}
     - SĐT: {{order_info.customer_phone}}
     - Địa chỉ: {{order_info.customer_address}}
     - Sản phẩm: {{order_info.product_requirement}}
     - Thanh toán: COD

     Nhân viên VHN sẽ liên hệ xác nhận trong thời gian sớm nhất...
     ```
   - **Python** – Save `old_order_customer_information`:
     ```python
     output = "customer name: " + '''{{order_info.customer_name}}'''
     output = output + "   \n   customer phone: " + '''{{order_info.customer_phone}}'''
     output = output + "   \n   customer address: " + '''{{order_info.customer_address}}'''
     print(output)
     ```
   - **Set Var**: `session.extra.registration_chat_history = empty_str()`
   - **Session Save**
   - **Clear Topic**

   **False:**
   - **Recall** (max_loop=10) → chờ User xác nhận ở turn tiếp theo

## 3.5. Xây dựng Flow Nhân sự nội bộ (`internal_staff`) – ⚠️ NÂNG CẤP

### Block 1: Save Human Input

### Block 2: AI QnA – Phân tích xác thực

| Trường | Giá trị |
|--------|---------|
| **Enable JSON Mode** | ✅ ON |
| **Variable to save** | `ai_auth_reply` |
| **Temperature** | `0.3` |

**Instruction:**
```
Kiểm tra User đã cung cấp Bộ phận + Mã NV chưa? Phân tích toàn bộ chat history + tin nhắn mới nhất.

Nếu CHƯA đủ:
- JSON: {"employee_id": "", "department": "", "need_more_info": true}
- Hỏi: "Dạ, để em hỗ trợ thông tin này, Anh/Chị vui lòng cho em xin Bộ phận và Mã số nhân viên ạ. Ví dụ: 'Phòng Marketing - MKT001'."

Nếu ĐÃ đủ:
- JSON: {"employee_id": "<mã NV>", "department": "<phòng ban>", "need_more_info": false}

Lưu ý: Mã NV thường format chữ+số (MKT001, SALES12). Bộ phận: Marketing, Sales, Kinh doanh, Kế toán, Nhân sự, Kỹ thuật, R&D.

JSON only.
```

### Block 3: Set Var
| Variable | Expression |
|----------|------------|
| `auth_info` | `json.loads("{{ai_auth_reply}}")` |

### Block 4: If đã xác thực

Condition: `auth_info.employee_id != "" and auth_info.department != ""`

**True (đã đủ thông tin):**

1. **Set Var**: `session.extra.employee_id = auth_info.employee_id`
2. **Set Var**: `session.extra.employee_dept = auth_info.department`
3. **Set Var**: `session.extra.employee_authenticated = "yes"`
4. **Session Save** ← Lưu trạng thái để các lượt sau NV không phải khai báo lại
5. **AI QnA – Internal Reply**

   | Trường | Giá trị |
   |--------|---------|
   | **Knowledge Dataset UUID** | _(UUID `vhn_b2b_product`)_ – truy cập toàn bộ SP B2B + phác đồ |
   | **Variable to save** | `bot_reply` |
   | **Result Limit** | `5` |
   | **Max Tokens** | `1500` |

   **Instruction:** dùng `{{ session.extra.employee_dept }}` và `{{ session.extra.employee_id }}` trong reply. Cho phép trả lời:
   - Liệt kê SP key của dòng (Unstress, Bio Phyto...)
   - Thống kê SP theo vendor
   - Phác đồ điều trị chuyên sâu

6. **Clear Topic**

**False (chưa đủ thông tin):**
- **Bot Send Text**: "Dạ, để em hỗ trợ thông tin nội bộ, Anh/Chị vui lòng cho em xin Bộ phận và Mã số nhân viên ạ. Ví dụ: 'Phòng Marketing - MKT001'."
- _(KHÔNG Clear Topic – chờ User cung cấp ở turn sau)_

> **Lưu ý quan trọng:** Vì có `session.extra.employee_authenticated`, nếu sau này muốn skip xác thực khi NV đã được xác thực trong session hiện tại, có thể thêm 1 block If ở đầu flow kiểm tra `session.extra.employee_authenticated == "yes"` để skip Block 2-3.

## 3.6. ⚠️ MỚI: Filter Bot Reply TOP-LEVEL (sau Flows Switch)

> **Đây là điểm thay đổi LỚN nhất so với bản tutorial cũ.**
>
> Trong bản cũ, mỗi flow có 1 block Filter Bot Reply riêng. Theo pattern Shegan (`ai_sales_agent.txt` block `ef8c9df971087e605aef715248c32763` trở đi), Filter Bot Reply phải đặt ở **TOP-LEVEL** – tức là **sau Flows Switch**, ở level cùng với Session Manager / Router / Flows Switch.
>
> **Ưu điểm:** Chỉ khai báo 1 lần, áp dụng cho TẤT CẢ output của TẤT CẢ flow. Tiết kiệm rất nhiều block.

Sau Flows Switch trong Mindflow, kéo thả 5 block **Bot Reply Filter** liên tiếp:

| # | Regex | Replace | Mục đích |
|---|-------|---------|----------|
| 1 | `(?:Tôi\|tôi)` | `em` | Sửa "tôi" → "em" |
| 2 | `(?:chúng tôi\|Chúng tôi\|chúng em\|Chúng em\|chúng mình\|Chúng mình)` | `bên em` | Sửa "chúng tôi" → "bên em" |
| 3 | `(?:trợ lý ảo\|chatbot\|Chatbot\|bot\|Bot\| AI )` | ` tư vấn viên ` | Sửa "chatbot/AI" → "tư vấn viên" |
| 4 | `(?:bạn\|Bạn)` | `Anh/Chị` | Sửa "bạn" → "Anh/Chị" |
| 5 | `(?:tôi không biết\|tôi không có thông tin\|em không biết)` | `em chưa có thông tin chi tiết về phần này` | Mềm hóa khi AI bí |

## 3.7. TEST TOÀN BỘ VỚI 14 SP

### 3.7.1. Test Guardrails (QUAN TRỌNG)

| # | Tình huống | Kỳ vọng |
|---|------------|---------|
| 1 | Khách B2C hỏi "Cho mình mua Step 3 Probiotic Peel" | AI từ chối: "Dạ, SP này là dòng chuyên nghiệp cần thực hiện tại Spa..." → gợi ý SP B2C tương đương |
| 2 | Khách B2B hỏi "Giá sỉ bao nhiêu?" | AI từ chối báo giá sỉ, xin Tên+SĐT+Tên cơ sở |
| 3 | Hỏi SP thiếu giá ("Total Serenity Serum giá nhiêu?") | AI dùng mẫu: "Dạ, sản phẩm... có chương trình ưu đãi đặc biệt, để lại SĐT..." |
| 4 | Hỏi nội bộ không cung cấp Mã NV ("Liệt kê SP key của Unstress") | AI yêu cầu Bộ phận + Mã NV |
| 5 | Hỏi "Bạn là ai?" | AI: "em là chuyên viên tư vấn của Y dược VHN" (KHÔNG nói chatbot/AI – nhờ filter) |
| 6 | NV B2B đã xác thực hỏi tiếp câu thứ 2 | Skip xác thực, trả lời thẳng (nhờ `employee_authenticated` trong session) |

### 3.7.2. Test End-to-End B2C (8 bước)

| Bước | Bạn nhắn | AI phải làm |
|------|----------|-------------|
| 1 | "Chào shop" | Chào hỏi, xưng "em", hỏi sàng lọc B2B/B2C |
| 2 | "Da mình bị mụn, tư vấn giúp" | Chuyển sang b2c_consult, hỏi loại da |
| 3 | "Da dầu" | Hỏi tuổi |
| 4 | "28 tuổi, mới bị gần đây" | Hỏi tình trạng đặc biệt |
| 5 | "Không có gì đặc biệt" | Đề xuất routine + SP B2C (**KHÔNG có SP B2B**) |
| 6 | "Mình lấy sản phẩm đó" | Chuyển sang luồng order (Set Topic → Recall). AI hỏi Tên+SĐT+Địa chỉ |
| 7 | "Lê Văn A, 0912345678, 123 Lê Lợi Q1 TPHCM" | Tổng hợp đơn bullet point, xin xác nhận |
| 8 | "Xác nhận" | Bot API Call ghi nhận đơn + cảm ơn + Clear Topic |

### 3.7.3. Test End-to-End B2B (5 bước)

| Bước | Bạn nhắn | AI phải làm |
|------|----------|-------------|
| 1 | "Mình muốn mua sản phẩm cho spa" | Chuyển sang b2b_consult, hỏi tên+cơ sở |
| 2 | "Anh Tùng, Spa Beauty ở quận 3" | Hỏi dịch vụ chính |
| 3 | "Trị mụn và phục hồi da" | Giới thiệu SP B2B (**KHÔNG có SP B2C**) |
| 4 | "Giá sỉ bao nhiêu?" | Từ chối báo giá, xin thông tin liên hệ |
| 5 | "0912345678, Spa Beauty, 100 Võ Văn Tần Q3" | API Call ghi nhận B2B_LEAD + cảm ơn |

### 3.7.4. Test Internal Staff

| Bước | Bạn nhắn | AI phải làm |
|------|----------|-------------|
| 1 | "Liệt kê sản phẩm key của dòng Unstress" | Yêu cầu Bộ phận + Mã NV |
| 2 | "Phòng Marketing - MKT001" | Xác thực OK → liệt kê SP key Unstress |
| 3 | "Còn Bio Phyto thì sao?" | Skip xác thực (do `employee_authenticated = yes`), trả lời thẳng |

### 3.7.5. Test Safety Net (recall_counter)

Khó test trực tiếp, nhưng có thể:
- Mở Testing Playground → Raw Output
- Nhắn 1 câu khiến AI parse JSON sai liên tục
- Xem `session.recall_counter` có tăng không
- Khi vượt 3 → AI gửi "Em vừa gặp lỗi đường truyền..."

## 3.8. Nạp full 240+ SP

**CHỈ thực hiện sau khi 14 SP chạy mượt mà!**

1. Vào Book `vhn_b2b_product` → Datasource `b2b_products`
2. Thay nội dung 7 SP → nội dung đầy đủ 98 SP từ `datasource_b2b_products.txt`
3. **Save & Process** → đợi xử lý

4. Vào Book `vhn_b2c_product` → Datasource `b2c_products`
5. Thay nội dung 7 SP → nội dung đầy đủ 142 SP từ `datasource_b2c_products.txt`
6. **Save & Process** → đợi xử lý

7. **Quick Test lại** trên cả 2 Book → đảm bảo kết quả vẫn chính xác
8. **Test regression** end-to-end: chạy lại toàn bộ kịch bản test để đảm bảo không bị hỏng

---

# TRIỂN KHAI & BÀN GIAO

## 4.1. Deploy to Production

1. Trong giao diện Agent → click **Deploy to Production**
2. AI Agent được xuất bản

## 4.2. Tích hợp lên Zalo / Facebook (Integration Browser)

### 4.2.1. Cài đặt Integration Browser

1. Tải Integration Browser từ Conductify
2. Mở ứng dụng → trang **Profiles**
3. Click **Add** → nhập tên `VHN_Zalo_1` → **Create**

### 4.2.2. Tích hợp Zalo

1. Chọn Profile `VHN_Zalo_1`
2. Đăng nhập Zalo trên Integration Browser
3. Cấu hình kết nối AI Agent
4. Test: Nhắn tin qua Zalo → AI Agent phản hồi

### 4.2.3. Tích hợp Facebook Messenger

1. Tạo Profile mới `VHN_Facebook_1`
2. Đăng nhập Facebook → kết nối Fanpage
3. Test: Nhắn tin qua Messenger → AI Agent phản hồi

## 4.3. Bàn giao AI CRM

Hướng dẫn VHN sử dụng AI CRM tại **https://hub.conductify.ai/**:

### Dashboard
- Thấy Agent "Y Dược VHN Assistant" đã Published
- Nút OPEN: mở chat standalone để test

### Tab CRM – Quản lý hội thoại
- Tìm kiếm theo kênh (Zalo/Facebook/Website), thời gian
- **Manual mode:** Bật khi AI chưa xử lý được → nhân viên tự nhắn
- Phân biệt: "Send by AI" vs "Send by Human"

### Tab Q&A – Chỉnh sửa kiến thức
- Thêm/sửa/xóa cặp Q&A trực tiếp (không cần vào Studio)

### Tab Integrations
- **Public URL:** Link chat standalone → nhúng vào website
- **Web Embed:** Mã nhúng AI Agent vào website VHN

### Tab Contact list – Xem đơn hàng & Lead
- Tất cả đơn B2C + lead B2B đã ghi nhận (filter theo `full_field.type`: `B2C_ORDER` hoặc `B2B_LEAD`)
- Hỗ trợ: tìm kiếm, phân trang, **xuất CSV** để báo cáo

---

# CHECKLIST TỔNG HỢP

## Trước khi bắt đầu
- [ ] Làm sạch vendor name Floslek (3 SP)
- [ ] Xử lý 66 SP thiếu giá → ghi "LIÊN HỆ"
- [ ] Chuẩn bị file CSV QnA (237 cặp)
- [ ] Chuẩn bị 5 file datasource (.txt)

## Bước cuốn chiếu 1
- [ ] Tạo Agent "Y Dược VHN Assistant"
- [ ] Tạo Book `vhn_general_info` + 2-3 datasource
- [ ] Tạo Q&A Library `vhn_qna` + Import 237 cặp CSV
- [ ] Quick Test General + QnA → OK
- [ ] Ghi lại UUID (2 UUID)

## Bước cuốn chiếu 2
- [ ] Session Manager + Extra Fields JSON (20+ biến) – paste từ `ai.txt`
- [ ] **MỚI: Block If `session.recall_counter > 3`** (Safety net) – paste từ `ai.txt`
- [ ] Router: 10 topics + phrases
- [ ] Flows Switch: 10 flow gán topic
- [ ] Flow `greetings`: AI QnA + Clear Topic
- [ ] Flow `off_topic` + `company_info` + `brand_info` + `promotion`
- [ ] **MỚI: Flow `handover` nâng cấp:** AI Analyze + Set handover + API Notify + AI Reply
- [ ] **Test phân luồng 10 câu → ≥ 90% đúng**

## Bước cuốn chiếu 3
- [ ] Tạo Book `vhn_b2b_product` (7 SP + 2 datasource phác đồ) + `vhn_b2c_product` (7 SP)
- [ ] Quick Test B2B + B2C → OK
- [ ] Ghi lại UUID mới (4 UUID tổng)
- [ ] **Flow B2B nâng cấp:** saveHumanInput + AI Consult + Python save chat_history_b2b + Session Save + AI Check + Set b2b_info + Parallel YES/NO/EXIT
- [ ] **Flow B2C nâng cấp:** saveHumanInput + AI Consult + Python save chat_history_b2c + AI Extract Product + Save findproduct_data + AI Check status + Parallel READY/CONTINUE/EXIT
- [ ] **Flow Đặt hàng nâng cấp:** saveHumanInput + AI Parse JSON + If exit + Python check completeness + Nested If: NO → AI Ask + Save reg_history / YES → AI Check Confirmation + If yes → API + Success / no → Recall
- [ ] **Flow Nội bộ nâng cấp:** saveHumanInput + AI Auth + Set var + If authenticated → Save employee_id/dept/authenticated + Session Save + AI Reply / else → Bot Send yêu cầu xác thực
- [ ] **MỚI: 5 block Filter Bot Reply TOP-LEVEL (sau Flows Switch)**
- [ ] **Test Guardrails 6 kịch bản → 100% đúng**
- [ ] **Test E2E B2C 8 bước → pass**
- [ ] **Test E2E B2B 5 bước → pass**
- [ ] **Test Internal Staff 3 bước → pass**
- [ ] Nạp full 240+ SP
- [ ] Test regression sau nạp full

## Triển khai
- [ ] Deploy to Production
- [ ] Integration Browser: Zalo
- [ ] Integration Browser: Facebook (nếu cần)
- [ ] Bàn giao AI CRM cho VHN

---

# PHỤ LỤC: SO SÁNH MINDFLOW TRƯỚC & SAU NÂNG CẤP

| Thành phần | Bản cũ | Bản mới (theo Shegan pattern) |
|------------|--------|------------------------------|
| Safety net recall_counter | ❌ Không có | ✅ Block If ở đầu (sau Session Manager) |
| Filter Bot Reply | Đặt trong từng flow (5+ lần) | ✅ Đặt TOP-LEVEL (1 lần) |
| Save human input | ❌ Không có | ✅ Đầu mỗi flow phức tạp |
| Chat history buffer riêng | ❌ Chỉ dùng chat_history gốc | ✅ chat_history_b2b/_b2c/registration_chat_history |
| Extract product of interest | ❌ Không có | ✅ Trong flow b2c_consult |
| Old order info | ❌ Không có | ✅ session.extra.old_order_customer_information |
| Employee authenticated state | ❌ Phải khai báo mỗi turn | ✅ session.extra.employee_authenticated |
| Order confirmation pattern | ❌ Chỉ check completeness | ✅ Check completeness + AI Check Confirmation + Recall |
| Handover API notify staff | ❌ Chỉ trả lời text | ✅ Có Bot API Call notify staff |
| Topic Phrases | Chỉ ý nghĩa chung | ✅ + Tên SP cụ thể (Step 3, Cicaderm...) giúp Router phân chính xác |

---

> **Tài liệu tham chiếu:**
> - `requirements.md` – Yêu cầu chính thức từ sếp (14 SP, 5 đề xuất, flowchart)
> - `ai_sales_agent.txt` – Mindflow mẫu Shegan (đã nghiên cứu pattern)
> - `ai.txt` – Mindflow đang xây cho VHN (sẵn sàng import vào Conductify)
> - `plan.md` – Kế hoạch kỹ thuật chi tiết
> - `AI_Trainer_BaoCao_TongHop.docx` – Báo cáo tổng hợp kiến thức khóa học
