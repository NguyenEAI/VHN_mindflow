# TÀI LIỆU YÊU CẦU HUẤN LUYỆN AI AGENT (VHN)

> **(Dành cho AI Engineer)**  
> **Nguồn:** Yêu cầu từ sếp  
> **Nền tảng:** Conductify AI Studio  
> **Ngày tổng hợp:** 2026-06-18

---

## PHẦN 1: DANH SÁCH 14 SẢN PHẨM TIÊU BIỂU ĐỂ HUẤN LUYỆN THỬ NGHIỆM

Để AI Engineer dễ dàng kiểm tra logic phân luồng, chúng ta sẽ chọn ra **14 sản phẩm tiêu biểu** từ dòng sản phẩm nổi tiếng Christina Unstress (và một vài thương hiệu khác) được chia đều thành 2 nhóm: **B2B** (Sản phẩm chuyên nghiệp tại Salon/Spa - Cột `is_salon_product` là `True`) và **B2C** (Sản phẩm chăm sóc tại nhà - Cột `is_salon_product` là `False`).

> **Lưu ý cho AI Engineer:** Trong sheet Product, có tổng cộng **240 sản phẩm** đã được phân loại rõ ràng, gồm **98 sản phẩm B2B** và **142 sản phẩm B2C**. Dưới đây là 14 sản phẩm được chọn lọc để chạy thử nghiệm giai đoạn đầu.

### 1. Nhóm Sản Phẩm B2B (`is_salon_product = True`) – Dành cho Spa, Thẩm mỹ viện, Bệnh viện

Các sản phẩm này là các bước trị liệu chuyên nghiệp (thường có chữ "Step" hoặc dung tích lớn), đòi hỏi kỹ thuật viên thực hiện:

| ID | Tên sản phẩm | Mô tả | Giá |
|----|-------------|-------|-----|
| 1 | Christina - Unstress - Step 1: Gentle Cleansing Milk - 300ml | Sữa tẩy trang rửa mặt dành cho da nhạy cảm | 2,398,000 VNĐ |
| 2 | Christina - Unstress - Step 2: Revitalizing Toner - 300ml | Nước hoa hồng cân bằng, làm dịu và đổi mới da | 2,266,000 VNĐ |
| 3 | Christina - Unstress - Step 3: Probiotic peel - 250ml | Peel thanh lọc và đổi mới da dịu nhẹ | 7,282,000 VNĐ |
| 4 | Christina - Unstress - Step 4: Frangipani Concentrate - 300ml | Huyết thanh làm dịu bảo vệ da | 2,800,000 VNĐ |
| 5 | Christina - Unstress - Step 5: Total Serenity Serum - 100ml | Huyết thanh phục hồi và làm dịu da | 7,150,000 VNĐ |
| 6 | Christina - Unstress - Step 6a: Relaxing Massage Cream - 500ml | Kem massage dưỡng ẩm và phục hồi da | 3,300,000 VNĐ |
| 220 | Preime - SKIN RENEW Skin Renewal Solution | Dung dịch tái tạo da chuyên dụng | 6,600,000 VNĐ |

### 2. Nhóm Sản Phẩm B2C (`is_salon_product = False`) – Dành cho Khách hàng cá nhân sử dụng tại nhà

Các sản phẩm dưỡng da hàng ngày, dung tích nhỏ gọn, dễ sử dụng:

| ID | Tên sản phẩm | Mô tả | Giá |
|----|-------------|-------|-----|
| 11 | Christina - Unstress - Gentle Cleansing Milk - 300ml | Sữa tẩy trang rửa mặt cho da nhạy cảm | 1,900,000 VNĐ |
| 12 | Christina - Unstress - Stabilizing Toner - 300ml | Nước hoa hồng cân bằng, làm dịu da | 1,900,000 VNĐ |
| 13 | Christina - Unstress - Total Serenity Serum - 50ml | Huyết thanh phục hồi da nhạy cảm | 3,190,000 VNĐ |
| 14 | Christina - Unstress - Probiotic Day Cream SPF 15 - 50ml | Kem dưỡng ngày bảo vệ da | 3,410,000 VNĐ |
| 15 | Christina - Unstress - Harmonizing Night Cream - 50ml | Kem dưỡng phục hồi ban đêm | 2,860,000 VNĐ |
| 16 | Christina - Unstress - Replenishing Mask - 50ml | Mặt nạ phục hồi da nhạy cảm | 2,100,000 VNĐ |
| 191 | Ivatherm - Cicaderm Cream - 40ml | Kem phục hồi, hỗ trợ tái tạo da và ngăn ngừa sẹo | 715,000 VNĐ |

---

## PHẦN 2: CÁC ĐỀ XUẤT BỔ SUNG QUAN TRỌNG ĐỂ THIẾT LẬP AI AGENT HIỆU QUẢ

Để AI hoạt động thông minh, hiểu khách hàng và không đi sai hướng, bạn AI Engineer cần bổ sung các cấu hình và logic sau vào hệ thống:

### 1. Định hình Persona (Tính cách & Vai trò của AI)

- **Vai trò:** Chuyên viên tư vấn da liễu và chăm sóc khách hàng đại diện cho Công ty Y dược VHN.
- **Giọng điệu (Tone of voice):** Chuyên nghiệp, lịch sự, chuẩn y khoa, tận tâm và đáng tin cậy.
- **Xưng hô:** Sử dụng các từ xưng hô lịch sự như "Dạ, em chào Anh/Chị", "Y dược VHN xin phép được hỗ trợ..."

### 2. Logic Phân Luồng Khách Hàng (Routing Logic)

AI cần có khả năng sàng lọc đối tượng ngay từ những câu thoại đầu tiên để rẽ nhánh tư vấn phù hợp:

**Dấu hiệu nhận biết khách hàng B2B:**
- Khách chủ động nhắc đến: Spa, Thẩm mỹ viện, Clinic, Bệnh viện, Nhà thuốc, Đại lý.
- Khách hỏi về: Chính sách chiết khấu, mua sỉ, bảng giá đại lý, các bước trị liệu chuyên nghiệp (Step 1-10).

**Dấu hiệu nhận biết khách hàng B2C:**
- Khách hỏi mua lẻ, hỏi giá của 1 sản phẩm cụ thể để tự dùng.
- Khách mô tả tình trạng da cá nhân: da mụn, da nám, da nhạy cảm, cần tư vấn routine chăm sóc da tại nhà.

**Luồng bảo mật nội bộ (Nhân sự Công ty):**
- Như trong sheet Kịch bản bán hàng (dòng 94-96), nếu người dùng hỏi các câu hỏi mang tính chất nội bộ (Ví dụ: "Liệt kê các sản phẩm key của dòng Unstress"), AI **phải yêu cầu cung cấp Bộ phận và Mã số nhân viên** trước khi trả lời.

### 3. Quy tắc Đề xuất Sản phẩm Nghiêm ngặt (Guardrails)

- **Không râu ông nọ cắm cằm bà kia:** Tuyệt đối không đề xuất các sản phẩm B2B (các Step trị liệu chuyên nghiệp, peel mạnh như Step 3 Probiotic Peel) cho khách hàng B2C tự dùng tại nhà để tránh gây kích ứng hoặc tổn thương da cho khách.
- **Bảo mật giá sỉ:** Chỉ cung cấp giá bán lẻ (được ghi trong sheet Product). Tuyệt đối không tự bịa ra giá sỉ hoặc chiết khấu cho khách B2B. Đối với khách B2B, mục tiêu là **xin thông tin để chuyên viên kinh doanh liên hệ trực tiếp**.

### 4. Xử lý Dữ liệu Khuyết thiếu (Missing Data)

Trong sheet Product, một số sản phẩm có thể bị thiếu giá hoặc link hình ảnh. AI Engineer cần cấu hình:

- Nếu khách hỏi sản phẩm thiếu giá/link: AI **không được tự bịa ra thông tin** (hallucination).
- **Mẫu câu phản hồi:** "Dạ, sản phẩm [Tên sản phẩm] hiện đang có chương trình ưu đãi đặc biệt dành riêng cho từng thời điểm. Anh/Chị vui lòng để lại SĐT để em báo giá chính xác nhất kèm quà tặng kèm theo cho mình nhé ạ!"

### 5. Mục tiêu Đầu ra của Cuộc hội thoại (Conversion Goal)

AI cần hiểu rõ điểm kết thúc của mỗi luồng:

- **Với B2B:** Kết thúc bằng việc xin **Tên + SĐT + Tên cơ sở (Spa/Clinic) + Địa chỉ** để chuyển cho bộ phận Sales liên hệ tư vấn chính sách đại lý.
- **Với B2C:** Kết thúc bằng việc hướng dẫn khách chốt đơn, xin **Tên + SĐT + Địa chỉ giao hàng** để lên đơn bán lẻ.

---

## PHẦN 3: SƠ ĐỒ PHÂN LUỒNG TƯ VẤN (FLOWCHART DẠNG CHỮ)

*(AI Engineer có thể dùng sơ đồ này để thiết kế State Machine hoặc Prompt Routing)*

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
         -> AI hỏi khéo léo: "Dạ, không biết Anh/Chị đang cần tìm sản phẩm 
            để chăm sóc da tại nhà hay dùng cho dịch vụ tại Spa/phòng khám 
            của mình ạ?"


===================== LUỒNG B2B (ĐẠI LÝ / SPA) =====================

[BƯỚC 2: KHAI THÁC THÔNG TIN CƠ SỞ]
   |-- Hỏi tên khách, tên Spa/Phòng khám, khu vực hoạt động.
   |-- Hỏi về dịch vụ chính của Spa (Trị mụn, làm trắng, phục hồi...) 
       và thiết bị công nghệ cao đang dùng.

[BƯỚC 3: ĐỀ XUẤT GIẢI PHÁP CHUYÊN NGHIỆP]
   |-- Giới thiệu các dòng sản phẩm chuyên nghiệp (B2B - is_salon_product = True).
   |-- Nhấn mạnh vào hiệu quả trị liệu lâm sàng và uy tín thương hiệu 
       (Christina phân phối tại hơn 2000 bệnh viện/spa).

[BƯỚC 4: THU THẬP THÔNG TIN LIÊN HỆ]
   |-- AI khéo léo từ chối báo chiết khấu chi tiết qua chat.
   |-- Xin Tên + SĐT để Chuyên viên kinh doanh gọi điện 
       gửi bảng giá sỉ và chính sách đại lý. -> [KẾT THÚC]


===================== LUỒNG B2C (KHÁCH LẺ) =====================

[BƯỚC 2: KHAI THÁC TÌNH TRẠNG DA]
   |-- Hỏi về loại da (Dầu, khô, hỗn hợp), độ tuổi, 
       tình trạng mụn/nám hiện tại.
   |-- Hỏi về thói quen skincare hiện tại hoặc các lưu ý đặc biệt 
       (như có đang mang thai hay không).

[BƯỚC 3: ĐỀ XUẤT ROUTINE TẠI NHÀ]
   |-- Đề xuất các sản phẩm B2C (is_salon_product = False) phù hợp.
   |-- Giải thích công dụng chính, cách dùng và báo giá bán lẻ niêm yết.

[BƯỚC 4: CHỐT ĐƠN & THU THẬP THÔNG TIN GIAO HÀNG]
   |-- Thuyết phục khách hàng về hiệu quả phục hồi/điều trị của sản phẩm.
   |-- Xin Tên + SĐT + Địa chỉ để lên đơn giao hàng. -> [KẾT THÚC]
```

---

## LỜI KHUYÊN THÊM: THỰC HIỆN THEO CÁC BƯỚC CUỐN CHIẾU

**Bước 1:** Cấu hình AI đọc hiểu thông tin doanh nghiệp trong sheet **Company** và các câu hỏi thường gặp trong sheet **QnA** trước để AI có nền tảng kiến thức chung.

**Bước 2:** Huấn luyện AI nhận diện và phân luồng khách hàng (B2B vs B2C) bằng cách chạy thử các câu test mẫu (Ví dụ: "Mình muốn mua sỉ cho spa" vs "Da mình nhạy cảm lắm tư vấn giúp mình").

**Bước 3:** Đưa dữ liệu 14 sản phẩm thử nghiệm ở trên vào để AI học cách đề xuất đúng sản phẩm cho đúng đối tượng. Sau khi luồng này chạy mượt mà, mới nạp toàn bộ 240+ sản phẩm còn lại vào hệ thống.
