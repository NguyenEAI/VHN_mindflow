import re

c = open(r'c:\Users\Administrator\Desktop\Hoc_python\data\b2c_cleaned.txt', encoding='utf-8').read()
lines = c.count('\n')
size  = len(c.encode('utf-8'))

r0 = len(re.findall(r'\n### C\u00f4ng d\u1ee5ng\nN/A', c))
r1 = len(re.findall(r'\n### Ch\u1ec9 \u0111\u1ecbnh\nN/A', c))
r2 = len(re.findall(r'\n### H\u01b0\u1edbng d\u1eabn s\u1eed d\u1ee5ng\nN/A', c))
r3 = len(re.findall(r'\n### Key gi\u1edbi thi\u1ec7u s\u1ea3n ph\u1ea9m\nN/A', c))
r4 = len(re.findall(r'Link s\u1ea3n ph\u1ea9m:\*\* N/A', c))

out = open('verify_result.txt', 'w')
out.write(f'lines={lines}\nsize_kb={size/1024:.1f}\nCong_dung_NA={r0}\nChi_dinh_NA={r1}\nHuong_dan_NA={r2}\nKey_intro_NA={r3}\nLinks_NA={r4}\n')
out.close()
