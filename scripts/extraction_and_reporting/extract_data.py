"""
Extract data from [INPUT 2] Sheet thu thập thông tin VHN.xlsx
Generates:
 - vhn_qna.csv               (Q&A pairs, 2 cols: question, answer - UTF-8)
 - datasource_company.txt    (Company info)
 - datasource_brands.txt     (Brand info from "Giới thiệu 7 nhãn hàng")
 - datasource_b2b_products.txt (98 SP with is_salon_product=True)
 - datasource_b2c_products.txt (142 SP with is_salon_product=False)
 - datasource_phac_do.txt    (Phác đồ Christina + Christina+Máy)
"""

import pandas as pd
import csv
import os
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'C:\Users\Administrator\Desktop\Hoc_python'
SRC = os.path.join(ROOT, '[INPUT 2] Sheet thu thập thông tin VHN.xlsx')
OUT_DIR = os.path.join(ROOT, 'output_datasources')
os.makedirs(OUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# 1) vhn_qna.csv
# ---------------------------------------------------------------------------
def gen_qna():
    df = pd.read_excel(SRC, sheet_name='QnA', header=None)
    # Real data starts after row 11 (header 'question/answer' at index 11)
    qna = df.iloc[12:, [0, 1]].copy()
    qna.columns = ['question', 'answer']
    qna = qna.dropna(subset=['question', 'answer'])
    qna['question'] = qna['question'].astype(str).str.strip()
    qna['answer'] = qna['answer'].astype(str).str.strip()
    qna = qna[(qna['question'] != '') & (qna['answer'] != '')
              & (qna['question'].str.lower() != 'nan')
              & (qna['answer'].str.lower() != 'nan')]

    out = os.path.join(OUT_DIR, 'vhn_qna.csv')
    qna.to_csv(out, index=False, encoding='utf-8-sig',
               quoting=csv.QUOTE_ALL, lineterminator='\n')
    print(f'[OK] {out}  ({len(qna)} rows)')


# ---------------------------------------------------------------------------
# 2) datasource_company.txt
# ---------------------------------------------------------------------------
def gen_company():
    df = pd.read_excel(SRC, sheet_name='Company', header=None)
    lines = ['# THÔNG TIN DOANH NGHIỆP – CÔNG TY Y DƯỢC VHN', '']

    # Real info from row 15 onwards (PHẦN ĐIỀN THÔNG TIN)
    for i in range(15, len(df)):
        label = df.iloc[i, 0]
        value = df.iloc[i, 1]
        if pd.isna(label) or pd.isna(value):
            continue
        label = str(label).strip()
        value = str(value).strip()
        if value in ('', 'nan', 'Điền thông tin tại đây'):
            continue
        # Clean label (remove "(Bắt buộc)" / "(Tuỳ chọn)" markers)
        clean_label = (label.replace('(Bắt buộc)', '')
                            .replace('(Tuỳ chọn)', '')
                            .strip())
        lines.append(f'## {clean_label}')
        lines.append(value)
        lines.append('')

    out = os.path.join(OUT_DIR, 'datasource_company.txt')
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'[OK] {out}')


# ---------------------------------------------------------------------------
# 3) datasource_brands.txt
# ---------------------------------------------------------------------------
def gen_brands():
    df = pd.read_excel(SRC, sheet_name='Giới thiệu 7 nhãn hàng', header=None)
    lines = ['# GIỚI THIỆU 7 NHÃN HÀNG VHN PHÂN PHỐI', '']

    current_brand = None
    intro_buffer = []
    consult_buffer = []

    def flush():
        if current_brand:
            lines.append(f'## {current_brand}')
            lines.append('')
            if intro_buffer:
                lines.append('### Key giới thiệu:')
                lines.extend(intro_buffer)
                lines.append('')
            if consult_buffer:
                lines.append('### Key tư vấn:')
                lines.extend(consult_buffer)
                lines.append('')

    # Brand names identified in column 0 (uppercase)
    known_brands = {'CHRISTINA', 'IVATHERM', 'FLOSLEK', 'PHARMALIFE',
                    'SRS MESOTHERAPY', 'PREIME', 'DERMOAROMA',
                    'PURASOME', 'PEELING SYSTEM'}

    for i in range(1, len(df)):
        col0 = df.iloc[i, 0]
        col1 = df.iloc[i, 1]
        col3 = df.iloc[i, 3]

        c0 = str(col0).strip() if not pd.isna(col0) else ''
        c1 = str(col1).strip() if not pd.isna(col1) else ''
        c3 = str(col3).strip() if not pd.isna(col3) else ''

        # Detect brand header
        is_brand_header = False
        for b in known_brands:
            if c0.upper().startswith(b):
                is_brand_header = True
                break
        # Special case for Dermoaroma which appears mid-text
        if 'Dermoaroma' in c0 and 'có trụ sở' in c0:
            is_brand_header = True
            # treat first line of c0 as "DERMOAROMA" header,
            # and content as intro
            flush()
            current_brand = 'DERMOAROMA'
            intro_buffer = [c0]
            consult_buffer = [c3] if c3 and c3 != 'nan' else []
            continue

        if is_brand_header:
            flush()
            current_brand = c0
            intro_buffer = []
            consult_buffer = []
            if c1 and c1 != 'nan':
                intro_buffer.append(c1)
            if c3 and c3 != 'nan':
                consult_buffer.append(c3)
        else:
            if c1 and c1 != 'nan':
                intro_buffer.append(c1)
            if c3 and c3 != 'nan':
                consult_buffer.append(c3)

    flush()

    out = os.path.join(OUT_DIR, 'datasource_brands.txt')
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'[OK] {out}')


# ---------------------------------------------------------------------------
# 4 + 5) datasource_b2b_products.txt and b2c_products.txt
# ---------------------------------------------------------------------------
def clean_vendor(v):
    if pd.isna(v):
        return ''
    return str(v).replace('\n', ' ').replace('\t', ' ').strip()


def format_price(p):
    if pd.isna(p):
        return 'LIÊN HỆ'
    s = str(p).strip()
    if s in ('', 'nan'):
        return 'LIÊN HỆ'
    if s.upper() == 'LIÊN HỆ':
        return 'LIÊN HỆ'
    try:
        n = int(float(s))
        return f'{n:,} VNĐ'.replace(',', ',')
    except Exception:
        return s


def gen_products():
    df = pd.read_excel(SRC, sheet_name='Product', header=0)
    df['vendor'] = df['vendor'].apply(clean_vendor)

    b2b_lines = ['# DANH SÁCH SẢN PHẨM B2B – CHUYÊN NGHIỆP (is_salon_product = True)',
                 '# Dành cho Spa, Thẩm mỹ viện, Clinic, Bệnh viện', '']
    b2c_lines = ['# DANH SÁCH SẢN PHẨM B2C – HOMECARE (is_salon_product = False)',
                 '# Dành cho khách hàng cá nhân dùng tại nhà', '']
    unc_lines = ['# DANH SÁCH SẢN PHẨM CHƯA PHÂN LOẠI (is_salon_product = NaN)', '']

    b2b_count = b2c_count = unc_count = 0

    for _, row in df.iterrows():
        pid_raw = row.get('id', '')
        try:
            pid = str(int(float(pid_raw)))
        except Exception:
            pid = str(pid_raw)
        name = str(row.get('name', '')).strip()
        if not name or name == 'nan':
            continue
        vendor = clean_vendor(row.get('vendor', ''))
        price = format_price(row.get('price', None))
        full_desc = row.get('full_description', '')
        if pd.isna(full_desc):
            full_desc = ''
        full_desc = str(full_desc).strip()
        link_product = str(row.get('link_product', '')).strip()
        link_image = str(row.get('link_image', '')).strip()
        is_salon = row.get('is_salon_product', None)

        # Convert is_salon to bool/None
        if isinstance(is_salon, bool):
            is_salon_bool = is_salon
        elif pd.isna(is_salon):
            is_salon_bool = None
        else:
            s = str(is_salon).strip().lower()
            if s == 'true':
                is_salon_bool = True
            elif s == 'false':
                is_salon_bool = False
            else:
                is_salon_bool = None

        block = ['---']
        block.append(f'ID: {pid}')
        block.append(f'Tên: {name}')
        block.append(f'Vendor: {vendor}')
        block.append(f'Giá: {price}')
        if is_salon_bool is True:
            block.append('Loại: B2B (Sản phẩm chuyên nghiệp - is_salon_product = True)')
        elif is_salon_bool is False:
            block.append('Loại: B2C (Sản phẩm homecare - is_salon_product = False)')
        else:
            block.append('Loại: Chưa phân loại')
        if full_desc and full_desc != 'nan':
            block.append(f'Mô tả chi tiết:\n{full_desc}')
        if link_product and link_product != 'nan':
            block.append(f'Link sản phẩm: {link_product}')
        if link_image and link_image != 'nan':
            block.append(f'Link ảnh: {link_image}')
        block.append('')

        text = '\n'.join(block)

        if is_salon_bool is True:
            b2b_lines.append(text)
            b2b_count += 1
        elif is_salon_bool is False:
            b2c_lines.append(text)
            b2c_count += 1
        else:
            unc_lines.append(text)
            unc_count += 1

    out_b2b = os.path.join(OUT_DIR, 'datasource_b2b_products.txt')
    out_b2c = os.path.join(OUT_DIR, 'datasource_b2c_products.txt')
    with open(out_b2b, 'w', encoding='utf-8') as f:
        f.write('\n'.join(b2b_lines))
    with open(out_b2c, 'w', encoding='utf-8') as f:
        f.write('\n'.join(b2c_lines))
    print(f'[OK] {out_b2b}  ({b2b_count} SP B2B)')
    print(f'[OK] {out_b2c}  ({b2c_count} SP B2C)')
    if unc_count:
        out_unc = os.path.join(OUT_DIR, 'datasource_uncategorized_products.txt')
        with open(out_unc, 'w', encoding='utf-8') as f:
            f.write('\n'.join(unc_lines))
        print(f'[OK] {out_unc}  ({unc_count} SP chưa phân loại)')


# ---------------------------------------------------------------------------
# 6) datasource_phac_do.txt – combine 2 sheets
# ---------------------------------------------------------------------------
def gen_phac_do():
    lines = ['# PHÁC ĐỒ TRỊ LIỆU CHRISTINA & PHỐI HỢP MÁY CÔNG NGHỆ CAO', '']

    # --- Phác đồ Christina ---
    df1 = pd.read_excel(SRC, sheet_name='Phác đồ của thương hiệu Christi', header=None)
    lines.append('## PHẦN 1: PHÁC ĐỒ CHRISTINA THUẦN SẢN PHẨM')
    lines.append('')
    # row 0 is header, data starts row 1
    header = [str(x).strip() for x in df1.iloc[0].tolist()]
    # Use the header columns
    current_lieutrinh = None
    current_chidi = None
    current_tacdung = None

    for i in range(1, len(df1)):
        row = df1.iloc[i]
        stt = row[0]
        ten = row[1]
        tac_dung = row[2]
        chi_dinh = row[3]
        san_pham = row[4]
        cach_dung = row[5]
        ghi_chu = row[6] if len(row) > 6 else None

        if not pd.isna(ten) and str(ten).strip() and str(ten).strip() != 'nan':
            current_lieutrinh = str(ten).strip()
            current_tacdung = str(tac_dung).strip() if not pd.isna(tac_dung) else ''
            current_chidi = str(chi_dinh).strip() if not pd.isna(chi_dinh) else ''
            lines.append('---')
            lines.append(f'### Liệu trình: {current_lieutrinh}')
            if current_tacdung and current_tacdung != 'nan':
                lines.append(f'**Tác dụng:** {current_tacdung}')
            if current_chidi and current_chidi != 'nan':
                lines.append(f'**Chỉ định:** {current_chidi}')
            lines.append('')
            lines.append('**Sản phẩm và cách dùng:**')

        if not pd.isna(san_pham) and str(san_pham).strip() and str(san_pham).strip() != 'nan':
            sp = str(san_pham).strip().replace('\n', ' ')
            cd = str(cach_dung).strip() if not pd.isna(cach_dung) else ''
            gc = str(ghi_chu).strip() if (ghi_chu is not None and not pd.isna(ghi_chu)) else ''
            lines.append(f'- **SP:** {sp}')
            if cd and cd != 'nan':
                lines.append(f'  **Cách dùng:** {cd}')
            if gc and gc != 'nan':
                lines.append(f'  **Ghi chú:** {gc}')
    lines.append('')

    # --- Phác đồ Christina + Máy ---
    df2 = pd.read_excel(SRC, sheet_name='Phác đồ Christina kết hợp với M', header=None)
    lines.append('## PHẦN 2: PHỐI HỢP PHÁC ĐỒ CHRISTINA VỚI MÁY CÔNG NGHỆ CAO')
    lines.append('')

    current_line = None
    for i in range(1, len(df2)):
        row = df2.iloc[i]
        line_name = row[0]
        buoc = row[1]
        ten_sp = row[2]
        tg = row[3]
        cach = row[4]
        gc = row[5] if len(row) > 5 else None

        ln = str(line_name).strip() if not pd.isna(line_name) else ''
        if ln and ln != 'nan' and ln != 'Bước':
            current_line = ln.replace('\n', ' ')
            lines.append('---')
            lines.append(f'### Phác đồ: {current_line}')
            lines.append('')

        if not pd.isna(buoc) and str(buoc).strip() and str(buoc).strip() != 'nan':
            step = str(buoc).strip().replace('\n', ' ')
            sp = str(ten_sp).strip().replace('\n', ' ') if not pd.isna(ten_sp) else ''
            time_ = str(tg).strip() if not pd.isna(tg) else ''
            cd = str(cach).strip() if not pd.isna(cach) else ''
            note = str(gc).strip() if (gc is not None and not pd.isna(gc)) else ''
            lines.append(f'- **Bước {step}**')
            if sp and sp != 'nan':
                lines.append(f'  Sản phẩm: {sp}')
            if time_ and time_ != 'nan':
                lines.append(f'  Thời gian: {time_}')
            if cd and cd != 'nan':
                lines.append(f'  Cách dùng: {cd}')
            if note and note != 'nan':
                lines.append(f'  Ghi chú: {note}')
    lines.append('')

    out = os.path.join(OUT_DIR, 'datasource_phac_do.txt')
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'[OK] {out}')


if __name__ == '__main__':
    print('=== Extracting VHN data ===')
    gen_qna()
    gen_company()
    gen_brands()
    gen_products()
    gen_phac_do()
    print('=== Done ===')
    print(f'Output dir: {OUT_DIR}')
