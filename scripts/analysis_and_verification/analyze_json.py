import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
data = json.load(open('VHN_fixing.json', encoding='utf-8'))

print("="*70)
print("PHÂN TÍCH TOKEN CHI TIẾT THEO TỪNG TIN NHẮN (9 TIN)")
print("="*70)

# Messages from test.txt
messages = [
    ("hello", "greetings", False),                     # Msg 1
    ("anh muốn hỏi về công ty mình", "qna", False),   # Msg 2
    ("Bên em phân phối sản phẩm của các thương hiệu nào ?", "qna", False),  # Msg 3
    ("Ừa em giới thiệu lịch sử của công ty đi em", "qna", False),  # Msg 4
    ("Cho anh hỏi giá christina unstress step 1 đi em", "recommend_product", True),  # Msg 5
    ("da anh bị mụn viêm nhiều quá em tư vấn sản phâm cho anh với", "gather_requirement", False),  # Msg 6
    ("Da anh da dầu và mụn viêm nhiều em ạ", "gather_requirement", False),  # Msg 7
    ("anh thường rửa mặt và bôi kem chống nắng thôi em", "gather_requirement", False),  # Msg 8
    ("anh không biết thương hiệu nào cả", "recommend_product", True),  # Msg 9
]

# Const sizes after optimization
const_sizes = {
    'company_name': 10, 'company_contact': 448, 'company_branch': 0,
    'assistant_role': 666, 'assistant_skill': 229, 'assistant_scope': 102,
    'assistant_tone': 989, 'vn_pronoun': 924, 'assistant_language_ability': 394,
    'category': 48, 'product_service_list': 517, 'product_list': 0,
    'treatment': 4063, 'agency': 115,
    'spa_in4': 243, 'spa': 237, 'phong_kham_in4': 212, 'phong_kham': 228,
    'tham_my_vien_in4': 336, 'tham_my_vien': 184,
    'benh_vien_in4': 281, 'benh_vien': 212,
    'he_thong_nha_thuoc_in4': 264, 'he_thong_nha_thuoc': 174,
}

# LLM node sizes (instruction only, before var expansion)
node_info = {
    'MANAGER': {'instr_chars': 16960, 'model': 'gpt-4o-mini', 'limit': 2, 'max_tok': 1000},
    'Query Data': {'instr_chars': 5620, 'model': 'gpt-4o-mini', 'limit': 2, 'max_tok': 1000},
    'Analysis': {'instr_chars': 2031, 'model': 'gpt-4o-mini', 'limit': 2, 'max_tok': 1000},
    'Greetings': {'instr_chars': 3070, 'model': 'gpt-4o-mini', 'limit': 5, 'max_tok': 1000},
    'QnA': {'instr_chars': 6588, 'model': 'gpt-4o-mini', 'limit': 10, 'max_tok': 2500},
    'Gather': {'instr_chars': 4782, 'model': 'gpt-4o', 'limit': 5, 'max_tok': 2500},
    'Recommend': {'instr_chars': 7218, 'model': 'gpt-4o', 'limit': 5, 'max_tok': 2000},
    'Handover': {'instr_chars': 2483, 'model': 'gpt-4o-mini', 'limit': 5, 'max_tok': 200},
    'Offtopic': {'instr_chars': 2419, 'model': 'gpt-4o-mini', 'limit': 5, 'max_tok': 1000},
    'Thank_you': {'instr_chars': 1586, 'model': 'gpt-4o-mini', 'limit': 5, 'max_tok': 1000},
}

# MANAGER always runs. Its instruction has MANY embedded vars.
# Let's estimate MANAGER expanded instruction size
mgr_vars_chars = sum([
    const_sizes['agency'], const_sizes['benh_vien'], const_sizes['benh_vien_in4'],
    const_sizes['category'], const_sizes['company_name'],
    const_sizes['he_thong_nha_thuoc'], const_sizes['he_thong_nha_thuoc_in4'],
    const_sizes['phong_kham'], const_sizes['phong_kham_in4'],
    const_sizes['spa'], const_sizes['spa_in4'],
    const_sizes['tham_my_vien'], const_sizes['tham_my_vien_in4'],
    const_sizes['treatment'],
    const_sizes['product_service_list'],
    500,  # session vars (previous_manager_decision, product_wishlist) estimated
])
mgr_total = 16960 + mgr_vars_chars
print(f"\nMANAGER instruction (template): 16,960 chars")
print(f"MANAGER vars expanded: +{mgr_vars_chars} chars")
print(f"MANAGER TOTAL instruction: {mgr_total} chars (~{mgr_total//4} tokens)")
print(f"MANAGER + 2 chat history messages (~400 chars): ~{(mgr_total+400)//4} tokens")
print(f"")

# Estimate per-message breakdown
total_all = 0
print("-"*70)
for i, (msg, phase, needs_product) in enumerate(messages, 1):
    print(f"\nTin nhắn {i}: \"{msg[:50]}...\"")
    print(f"  Phase: {phase} | Need product info: {needs_product}")
    
    msg_total = 0
    
    # Always: MANAGER call
    mgr_input = (mgr_total + 400) // 4  # + chat history
    msg_total += mgr_input
    print(f"  [1] MANAGER: ~{mgr_input} tokens (gpt-4o-mini)")
    
    # If needs product info
    if needs_product:
        qd_input = (5620 + 500) // 4  # query data + session vars
        msg_total += qd_input
        print(f"  [2] Query Data: ~{qd_input} tokens (gpt-4o-mini)")
        
        analysis_input = (2031 + 2000) // 4  # analysis + API response data
        msg_total += analysis_input
        print(f"  [3] Analysis: ~{analysis_input} tokens (gpt-4o-mini)")
    
    # Phase-specific node
    if phase == 'greetings':
        # Greetings has lots of vars: role, skill, scope, tone, vn_pronoun, language, contact, agency
        gv = sum([const_sizes['assistant_role'], const_sizes['assistant_skill'],
                   const_sizes['assistant_scope'], const_sizes['assistant_tone'],
                   const_sizes['vn_pronoun'], const_sizes['assistant_language_ability'],
                   const_sizes['company_contact'], const_sizes['agency'],
                   const_sizes['product_service_list'], 200])  # session vars
        gt = (3070 + gv + 400) // 4  # + chat history
        msg_total += gt
        print(f"  [4] Greetings: ~{gt} tokens (gpt-4o-mini)")
    elif phase == 'qna':
        qv = sum([const_sizes['assistant_role'], const_sizes['assistant_skill'],
                  const_sizes['assistant_tone'], const_sizes['vn_pronoun'],
                  const_sizes['assistant_language_ability'], const_sizes['company_contact'],
                  const_sizes['treatment'], const_sizes['product_service_list'], 500])  # session + RAG
        # limit=10 means up to 10 chat history messages!
        chat_hist = min(i * 200, 10 * 200)  # growing history
        qt = (6588 + qv + chat_hist) // 4
        msg_total += qt
        print(f"  [4] QnA: ~{qt} tokens (gpt-4o-mini) [limit=10, chat_hist~{chat_hist} chars]")
    elif phase == 'gather_requirement':
        gv = sum([const_sizes['assistant_role'], const_sizes['assistant_skill'],
                  const_sizes['assistant_tone'], const_sizes['vn_pronoun'],
                  const_sizes['assistant_language_ability'], const_sizes['company_contact'],
                  const_sizes['agency'], const_sizes['product_service_list'], 500])
        chat_hist = min(i * 200, 5 * 200)
        gt = (4782 + gv + chat_hist) // 4
        msg_total += gt
        print(f"  [4] Gather Req: ~{gt} tokens (gpt-4o) [limit=5, chat_hist~{chat_hist} chars]")
    elif phase == 'recommend_product':
        rv = sum([const_sizes['assistant_role'], const_sizes['assistant_skill'],
                  const_sizes['assistant_tone'], const_sizes['vn_pronoun'],
                  const_sizes['assistant_language_ability'], const_sizes['company_contact'],
                  const_sizes['product_service_list'], 3000])  # product_information from API
        chat_hist = min(i * 200, 5 * 200)
        rt = (7218 + rv + chat_hist) // 4
        msg_total += rt
        print(f"  [4] Recommend: ~{rt} tokens (gpt-4o) [limit=5, chat_hist~{chat_hist} chars]")
    
    # RAG/Knowledge call adds tokens for knowledge_from_rag
    if phase in ['qna']:
        rag_tokens = 500  # estimated RAG retrieval
        msg_total += rag_tokens
        print(f"  [+] RAG Knowledge: ~{rag_tokens} tokens")
    
    print(f"  >>> TỔNG TIN NHẮN {i}: ~{msg_total} tokens")
    total_all += msg_total

print(f"\n{'='*70}")
print(f"TỔNG ƯỚC TÍNH 9 TIN NHẮN: ~{total_all} tokens")
print(f"THỰC TẾ (theo dashboard): 305,284 tokens")
print(f"CHÊNH LỆCH: {305284 - total_all} tokens ({(305284-total_all)*100//305284}%)")
print(f"")
print(f"==> PHẦN CHÊNH LỆCH LÀ DO:")
print(f"  1. Knowledge Base (RAG) trả về text dài (không kiểm soát)")
print(f"  2. API Product Data trả về nhiều sản phẩm")
print(f"  3. Chat history tích lũy (bot reply dài)")
print(f"  4. Recall/Retry khi LLM output sai format")
print(f"  5. Mỗi node QnA của Conductify tự thêm system prompt overhead")
