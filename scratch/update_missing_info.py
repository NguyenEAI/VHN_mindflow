import json

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Path to "If missing phone" node:
# data['sequence'][5]['branches']['order'][5]['branches']['false'][0]['branches']['true'][0]
if_missing = data['sequence'][5]['branches']['order'][5]['branches']['false'][0]['branches']['true'][0]

if if_missing.get('name') == 'If missing phone':
    if_missing['name'] = 'If missing info'
    if_missing['properties']['condition'] = 'order_info.customer_phone == "NOT-PROVIDED" or order_info.customer_name == "NOT-PROVIDED" or order_info.customer_address == "NOT-PROVIDED"'
    print("Updated If missing info condition!")

# Path to "Bot Send Text - Ask Missing":
ask_missing = if_missing['branches']['true'][0]
if ask_missing.get('name') == 'Bot Send Text - Ask Missing':
    ask_missing['properties']['text'] = 'Dạ, trước khi hoàn tất đơn hàng, Anh/Chị vui lòng bổ sung giúp em đầy đủ thông tin **Họ tên, SĐT và Địa chỉ giao hàng** (số nhà, đường, quận/huyện, tỉnh/thành) để nhân viên VHN liên hệ xác nhận chính xác nhé!'
    print("Updated Bot Send Text - Ask Missing text!")

with open(r'C:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Saved VHN_DauTien_Fixed.json successfully!")
