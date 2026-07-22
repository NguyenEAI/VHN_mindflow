# Kết quả test nhanh chatbot VHN — 10 câu hỏi tư vấn sản phẩm

Thời gian test: 2026-07-14 16:15–16:30 GMT+7  
Trang test: `https://chat.conductify.ai/?agentUuid=cd93b65b-c93a-4033-b590-1af34f5b6ca6`

## Tổng quan
## LƯU Ý : TẤT CẢ CÁC CÂU HỎI CỦA USER ĐỀU ĐƯỢC NHẮN TRÊN CÙNG SESSION.
Đã gửi 10 câu hỏi theo danh sách test. Kết quả: bot trả lời được nhiều câu sản phẩm cụ thể, nhưng có 4 lỗi đáng chú ý:

1. Context bị nhiễm giữa các câu vì test cùng một session.
2. Bot tự suy luận “an toàn cho phụ nữ mang bầu” ở nhiều câu, dù không có căn cứ.
3. Câu trị mụn lưng trả lời sai: báo chưa có sản phẩm, trong khi workflow có rule chọn `Christina - Rose De Mer- Peeling Soap - 30g`.
4. Câu agency/spa cuối bị lỗi prompt program: `Unterminated string starting at...`.

## Chi tiết từng câu

### 1. Da dầu, dễ nổi mụn ẩn

**User:** Chị da dầu, dễ nổi mụn ẩn thì bên em có sản phẩm nào phù hợp không?

**Bot:** Hỏi thêm thói quen chăm sóc da hiện tại.

**Đánh giá:** Tạm ổn nếu mục tiêu là khai thác thêm trước khi recommend. Nhưng user hỏi “có sản phẩm nào phù hợp không” nên có thể cân nhắc chuyển sang recommend nhanh hơn nếu muốn tăng sale.

---

### 2. Cicaderm

**User:** Cicaderm là của hãng nào? Sản phẩm này dùng để phục hồi da sau treatment được không?

**Bot:** Trả lời Cicaderm thuộc Ivatherm, đưa đúng sản phẩm `Ivatherm - Cicaderm Cream - 40ml`, có ảnh, giá 715.000 VND, thành phần, công dụng, chỉ định, hướng dẫn, link.

**Đánh giá:** Pass tốt.

**Ghi chú UX:** Link sản phẩm có thể mở sang trang sản phẩm nếu click nhầm, nên test UI cần tránh click link khi đang nhập tiếp.

---

### 3. Serum cấp ẩm phục hồi Ivatherm

**User:** Em tư vấn cho chị serum cấp ẩm phục hồi da của Ivatherm với.

**Bot:** Gợi ý `Ivatherm - Aquafil - Hydra Hydrating Serum - 30ml`, có ảnh, giá 980.000 VND, thành phần, công dụng, chỉ định, hướng dẫn, link.

**Đánh giá:** Pass.

**Lưu ý:** Bot có câu “phù hợp với da dầu và dễ nổi mụn” do nhiễm context từ câu 1. Nếu test độc lập, cần reset session.

---

### 4. Nám và xỉn màu lâu năm

**User:** Da chị bị nám và xỉn màu lâu năm, bên em có sản phẩm nào hỗ trợ không?

**Bot:** Hỏi thêm lý do nám/xỉn màu: ánh nắng, nội tiết tố, yếu tố khác.

**Đánh giá:** Pass theo rule workflow: nám/xỉn màu phải hỏi thêm lý do trước.

---

### 5. Mang bầu dùng Unstress

**User:** Chị đang mang bầu 4 tháng, dùng dòng Unstress được không em?

**Bot:** Trả lời nên thận trọng, dòng Unstress chủ yếu làm dịu/phục hồi da nhạy cảm, nên tham khảo bác sĩ trước khi dùng.

**Đánh giá:** Fail.

**Lý do:** Workflow có rule: dòng Unstress không dùng cho mẹ bầu/phụ nữ có thai/đang cho con bú. Bot không nói rõ “không dùng”, cũng không handover mạnh.

---

### 6. Trị mụn lưng

**User:** Bên em có sản phẩm nào trị mụn lưng không? Lưng chị bị mụn ẩn và thâm.

**Bot:** Báo hiện tại chưa có sản phẩm cụ thể để điều trị mụn lưng, khuyên vệ sinh vùng lưng, dùng sữa tắm dịu nhẹ, tẩy tế bào chết.

**Đánh giá:** Fail.

**Lý do:** Workflow có friendly reminder bắt buộc chọn `Christina - Rose De Mer- Peeling Soap - 30g` khi khách hỏi trị mụn lưng. Bot lại nói không có sản phẩm cụ thể.

---

### 7. Kem chống nắng cho da nhạy cảm

**User:** Chị muốn tìm kem chống nắng phù hợp cho da nhạy cảm, bên em có loại nào không?

**Bot:** Gợi ý:
- `Ivatherm - Ivapur - SPF50+ Anti-shine Fluid - 50ml`
- `Ivatherm - Sunlight Mat - SPF50+ Dry touch Fluid - 50ml`

Có giá, thành phần, công dụng, chỉ định, hướng dẫn, link.

**Đánh giá:** Pass về sản phẩm chống nắng.

**Lỗi nghiêm trọng:** Bot tự thêm câu “Cả hai sản phẩm đều rất phù hợp cho da nhạy cảm và an toàn cho phụ nữ mang bầu” dù user không hỏi mang bầu và không có căn cứ. Đây là nhiễm context + hallucination safety.

---

### 8. Sản phẩm cao cấp chăm sóc tại nhà

**User:** Chị muốn mua sản phẩm cao cấp để chăm sóc da tại nhà, em gợi ý giúp chị.

**Bot:** Gợi ý các sản phẩm Christina Unstress, ví dụ:
- `Christina - Unstress - Step 2: Revitalizing Toner - 300ml`
- `Christina - Unstress - Step 5: Total Serenity Serum - 100ml`

**Đánh giá:** Tạm pass về hướng chọn phân khúc cao cấp/Christina.

**Lưu ý:** Vì chạy cùng session sau câu mẹ bầu, kết quả có nguy cơ nhiễm context. Nên retest câu này trong session sạch.

---

### 9. Hỏi thêm sản phẩm khác

**User:** Còn sản phẩm nào khác không em? Chị muốn xem thêm lựa chọn.

**Bot:** Gợi ý thêm sản phẩm Christina Unstress:
- `Christina - Unstress - Step 6b: Multi Vitamin Supplement - 100ml`
- `Christina - Unstress - Step 8: Optimal hydration mask - 250ml`

**Đánh giá:** Pass một phần: có cung cấp thêm sản phẩm.

**Lỗi nghiêm trọng:** Lại tự nói “an toàn cho phụ nữ mang bầu”. Cần chặn câu này nếu không có dữ liệu xác thực.

---

### 10. Chủ spa muốn nhập sản phẩm phục hồi sau peel/laser

**User:** Anh là chủ spa, muốn nhập sản phẩm phục hồi da sau peel/laser cho khách thì bên em có dòng nào phù hợp?

**Bot:** Không trả lời nội dung. Hiện lỗi:

```text
Error in Prompt Program: Unterminated string starting at: line 1 column 119 (char 118)
```

**Đánh giá:** Fail/blocker.

**Lý do:** Có lỗi parse/prompt program ở nhánh agency hoặc handover. Cần kiểm tra template JSON/string escaping của prompt/API body ở luồng `agency_gather_info`.

## Kết luận nhanh

Các câu pass/tạm pass:
- Câu 1: tạm pass
- Câu 2: pass
- Câu 3: pass
- Câu 4: pass
- Câu 7: pass sản phẩm nhưng fail safety sentence
- Câu 8: tạm pass
- Câu 9: pass một phần

Các lỗi cần sửa ưu tiên:

1. **Unstress + mẹ bầu:** bắt buộc trả lời không dùng/không khuyến nghị và handover, không chỉ “tham khảo bác sĩ”.
2. **Mụn lưng:** phải map đúng sang `Christina - Rose De Mer- Peeling Soap - 30g`.
3. **Chặn hallucination thai kỳ:** không được tự nói sản phẩm “an toàn cho phụ nữ mang bầu” ở câu chống nắng/sản phẩm khác.
4. **Agency/spa lỗi prompt:** sửa lỗi `Unterminated string` ở nhánh agency/handover.
5. **Regression test nên reset session giữa các câu** để tránh nhiễm context.
