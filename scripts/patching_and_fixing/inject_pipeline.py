import json

def update_session(vhn_dt_data):
    session_node = vhn_dt_data['sequence'][0]
    extra_str = session_node['properties']['extra']
    extra_json = json.loads(extra_str)
    
    extra_json['product_wishlist'] = "Product List:"
    extra_json['product_information'] = "empty"
    extra_json['query_data'] = {"vendor": "none", "product_type": "none"}
    extra_json['previous_manager_decision'] = {
        "need_product_info": "no",
        "target_product": "NOT-PROVIDED"
    }
    extra_json['is_salon_product'] = 0
    
    session_node['properties']['extra'] = json.dumps(extra_json, ensure_ascii=False, indent=2)

def add_constants(vhn_dt_data, vhn_bk_data):
    sheet_block = next((n for n in vhn_bk_data['sequence'] if n.get('name') == 'Sheet'), None)
    api_url_block = next((n for n in vhn_bk_data['sequence'] if n.get('name') == 'api_url'), None)
    
    if sheet_block:
        vhn_dt_data['sequence'].insert(1, sheet_block)
    if api_url_block:
        search_data_node = next((n for n in api_url_block.get('sequence', []) if n.get('name') == 'Const [api_url_search_data]'), None)
        if search_data_node:
            new_api_block = {
                "id": "new_api_block_id",
                "componentType": "container",
                "type": "block",
                "name": "API Constants",
                "properties": {"hidden": False},
                "sequence": [search_data_node]
            }
            vhn_dt_data['sequence'].insert(2, new_api_block)

def build_product_pipeline(bk_data, branch_name):
    pipeline = []
    
    decide_node = {
        "id": f"{branch_name}_qna_decide",
        "type": "qna",
        "componentType": "task",
        "name": f"AI Decide {branch_name}",
        "properties": {
            "instruction": f"# Role\nAssistant là Manager quyết định xem trong tình huống này có cần tra cứu thông tin sản phẩm từ cơ sở dữ liệu hay không.\n\n# Task\nĐọc lịch sử trò chuyện và câu nói mới nhất của User.\nNếu User nhắc tới tên sản phẩm, dòng sản phẩm, thương hiệu, hoặc yêu cầu đề xuất sản phẩm -> cần thông tin sản phẩm.\nNếu User chỉ đang chào hỏi hoặc trả lời các thông tin khai thác nhu cầu chưa yêu cầu gợi ý -> không cần.\n\n# Output JSON\nTrả về JSON:\n{{\n  \"need_product_info\": \"yes\" hoặc \"no\"\n}}",
            "dataset_uuid": "", "dataset_qa_uuid": "", "rag_query": "", "limit": "2", "api_key": "",
            "knowledge": "{{ knowledge_from_rag }}", "knowledge_aware": False, "chat_history_aware": True,
            "human_input_aware": True, "varReply": "manager_decision", "temperature": "0.1",
            "max_tokens": "200", "stop": "", "stop_regex": "", "pattern": "", "json_mode": True,
            "multimodal_mode": False, "tools": "", "agent_loop": False, "llm_alt_model": "gpt-4o-mini"
        }
    }
    
    set_decision_node = {
        "id": f"{branch_name}_set_decision",
        "type": "setVar",
        "componentType": "task",
        "name": "Save Decision",
        "properties": {
            "varName": "session.extra.previous_manager_decision",
            "varValue": "json.loads(manager_decision)"
        }
    }
    
    query_node = {
        "id": f"{branch_name}_query_data",
        "type": "qna",
        "componentType": "task",
        "name": "GPT-4 Query Data",
        "properties": {
            "instruction": "Nhiệm vụ: đọc tin nhắn mới nhất và context, chọn vendor/product_type từ enum.\nChỉ trả JSON hợp lệ:\n{\n  \"vendor\": [\"christina\", \"floslek\", \"ivatherm\", \"dermoaroma\", \"preime\", \"pharmalife\", \"none\"],\n  \"product_type\": [\"serum\", \"cream\", \"cleanser\", \"antisun\", \"peel\", \"toner\", \"mask\", \"body\", \"none\"]\n}\nKhông tạo enum mới. Nếu không chắc, dùng [\"none\"].",
            "dataset_uuid": "", "dataset_qa_uuid": "", "rag_query": "", "limit": "2", "api_key": "",
            "knowledge": "{{ knowledge_from_rag }}", "knowledge_aware": False, "chat_history_aware": False,
            "human_input_aware": True, "varReply": "ai_query_data", "temperature": "0.1",
            "max_tokens": "200", "stop": "", "stop_regex": "", "pattern": "", "json_mode": True,
            "multimodal_mode": False, "tools": "", "agent_loop": False, "llm_alt_model": "gpt-4o-mini"
        }
    }
    
    set_query = {
        "id": f"{branch_name}_set_query",
        "type": "setVar",
        "componentType": "task",
        "name": "Set Query",
        "properties": {
            "varName": "session.extra.query_data",
            "varValue": "json.loads(ai_query_data)"
        }
    }
    
    api_call = {
        "id": f"{branch_name}_api_call",
        "type": "botAPICall",
        "componentType": "task",
        "name": "API CALL PRODUCT DATA",
        "properties": {
            "api_response_var_name": "api_call_product_data",
            "api_url": "{{api_url_search_data}}",
            "api_body": "{\n  \"bot_uuid\": \"{{ bot_uuid }}\",\n  \"channel_type\": \"{{ channel_type }}\",\n  \"channel_id\": \"{{ channel_id }}\",\n  \"thread_id\": \"{{ thread_id }}\",\n  \"user_msg_id\": \"{{ user_msg_id }}\",\n  \"vendor\": \"{{ session.extra.query_data.vendor[0] }}\",\n  \"product_type\": \"{{ session.extra.query_data.product_type[0] }}\",\n  \"sheet_url\": \"{{ sheet_url }}\",\n  \"is_salon_product\": " + ("true" if branch_name == "b2b_consult" else "false") + "\n}",
            "api_header": "{}",
            "api_method": "POST"
        }
    }
    
    set_api_raw = {
        "id": f"{branch_name}_set_api_raw",
        "type": "setVar",
        "componentType": "task",
        "name": "Set API Raw",
        "properties": {
            "varName": "api_raw_product_data",
            "varValue": "json.loads(api_call_product_data)"
        }
    }
    
    py_format_wishlist = {
        "id": f"{branch_name}_py_wishlist",
        "type": "python",
        "componentType": "task",
        "name": "Format Wishlist",
        "properties": {
            "varName": "session.extra.product_wishlist",
            "expression": "try:\n    PRODUCTS = api_raw_product_data[0].get('data', [])\n    if len(PRODUCTS) > 10: PRODUCTS = PRODUCTS[:10]\n    content = \"Danh sách SP:\\n\"\n    for p in PRODUCTS:\n        content += f\"- Tên: {p.get('name')}, Giá: {p.get('price')}\\n\"\n    print(content)\nexcept:\n    print('empty')"
        }
    }
    
    ai_analyze = {
        "id": f"{branch_name}_ai_analyze",
        "type": "qna",
        "componentType": "task",
        "name": "AI Analyze Product Names",
        "properties": {
            "instruction": "Product List:\n{{ session.extra.product_wishlist }}\n\nĐọc nhu cầu của khách hàng và chọn tối đa 3 sản phẩm phù hợp nhất từ Product List.\nChỉ trả JSON:\n{\"name\": [\"Tên SP 1\", \"Tên SP 2\"]}\nTUYỆT ĐỐI KHÔNG bịa tên sản phẩm ngoài danh sách.",
            "dataset_uuid": "", "dataset_qa_uuid": "", "rag_query": "", "limit": "2", "api_key": "",
            "knowledge": "{{ knowledge_from_rag }}", "knowledge_aware": False, "chat_history_aware": False,
            "human_input_aware": True, "varReply": "bot_analyze", "temperature": "0.1",
            "max_tokens": "200", "stop": "", "stop_regex": "", "pattern": "", "json_mode": True,
            "multimodal_mode": False, "tools": "", "agent_loop": False, "llm_alt_model": "gpt-4o-mini"
        }
    }
    
    set_analyze = {
        "id": f"{branch_name}_set_analyze",
        "type": "setVar",
        "componentType": "task",
        "name": "Set Analyze",
        "properties": {
            "varName": "product_analyze",
            "varValue": "json.loads(bot_analyze)"
        }
    }
    
    py_exact_match = {
        "id": f"{branch_name}_py_exact",
        "type": "python",
        "componentType": "task",
        "name": "Exact Match Info",
        "properties": {
            "varName": "session.extra.product_information",
            "expression": "try:\n    PRODUCTS = api_raw_product_data[0].get('data', [])\n    WISHLIST = product_analyze.get('name', [])\n    content = \"\"\n    for p in PRODUCTS:\n        title = str(p.get('name', '')).strip()\n        if title in WISHLIST:\n            content += f\"**{title}**\\n\"\n            if 'link_image' in p and p['link_image'] != 'N/A': content += f\"![Ảnh]({p['link_image']})\\n\"\n            if 'price' in p and p['price'] != 'N/A': content += f\"Giá: {p['price']} VNĐ\\n\"\n            if 'link_product' in p and p['link_product'] != 'N/A': content += f\"[Link]({p['link_product']})\\n\"\n            desc = str(p.get('full_description', '')).replace('\\n', ' ')\n            content += f\"Thông tin: {desc}\\n\\n\"\n    if not content: content = \"empty\"\n    print(content)\nexcept:\n    print('empty')"
        }
    }
    
    save_find_data = {
        "id": f"{branch_name}_save_find_data",
        "type": "setVar",
        "componentType": "task",
        "name": "Save findproduct_data",
        "properties": {
            "varName": "session.extra.findproduct_data",
            "varValue": "session.extra.product_information"
        }
    }
    
    product_if_node = {
        "id": f"{branch_name}_product_if",
        "type": "if",
        "componentType": "switch",
        "name": "If need product info",
        "properties": {
            "condition": "session.extra.previous_manager_decision.need_product_info == \"yes\""
        },
        "branches": {
            "true": [
                query_node, set_query, api_call, set_api_raw, py_format_wishlist, ai_analyze, set_analyze, py_exact_match, save_find_data
            ],
            "false": []
        }
    }
    
    pipeline.extend([decide_node, set_decision_node, product_if_node])
    return pipeline

def process():
    with open(r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(r'c:\Users\Administrator\Desktop\Hoc_python\VHN_backup.json', 'r', encoding='utf-8') as f:
        bk_data = json.load(f)
        
    update_session(data)
    add_constants(data, bk_data)
    
    fs = next((n for n in data['sequence'] if n.get('type') == 'flowSwitch'), None)
    if fs:
        # --- B2C CONSULT ---
        b2c_orig = fs['branches']['b2c_consult']
        save_human_b2c = b2c_orig[0]
        qna_b2c = b2c_orig[1]
        verify_url_b2c = b2c_orig[2]
        collect_history_b2c = b2c_orig[3]
        
        # We skip original extract product (b2c_orig[4], b2c_orig[5]) 
        # and directly take from [6] to end
        rest_b2c = b2c_orig[6:]
        
        qna_b2c['properties']['instruction'] += "\n\n# SOURCE OF TRUTH (PRODUCT INFORMATION)\nAssistant CHỈ ĐƯỢC PHÉP ĐỀ XUẤT SẢN PHẨM CÓ TRONG DANH SÁCH SAU ĐÂY:\n\"\"\" {{ session.extra.product_information }} \"\"\"\nNếu danh sách trống, hãy tiếp tục khai thác nhu cầu của khách hàng hoặc nói chưa tìm thấy sản phẩm phù hợp. TUYỆT ĐỐI KHÔNG BỊA SẢN PHẨM HOẶC LẤY SẢN PHẨM KHÔNG CÓ TRONG DANH SÁCH TRÊN."
        qna_b2c['properties']['knowledge_aware'] = False
        qna_b2c['properties']['knowledge'] = ""
        
        pipeline_b2c = build_product_pipeline(bk_data, 'b2c_consult')
        fs['branches']['b2c_consult'] = [save_human_b2c] + pipeline_b2c + [qna_b2c, verify_url_b2c, collect_history_b2c] + rest_b2c
        
        # --- B2B CONSULT ---
        b2b_orig = fs['branches']['b2b_consult']
        save_human_b2b = b2b_orig[0]
        qna_b2b = b2b_orig[1]
        rest_b2b = b2b_orig[2:]
        
        qna_b2b['properties']['instruction'] += "\n\n# SOURCE OF TRUTH (PRODUCT INFORMATION)\nAssistant CHỈ ĐƯỢC PHÉP ĐỀ XUẤT SẢN PHẨM CÓ TRONG DANH SÁCH SAU ĐÂY:\n\"\"\" {{ session.extra.product_information }} \"\"\"\nNếu danh sách trống, hãy tiếp tục khai thác nhu cầu của khách hàng hoặc nói chưa tìm thấy sản phẩm phù hợp. TUYỆT ĐỐI KHÔNG BỊA SẢN PHẨM HOẶC LẤY SẢN PHẨM KHÔNG CÓ TRONG DANH SÁCH TRÊN."
        qna_b2b['properties']['knowledge_aware'] = False
        qna_b2b['properties']['knowledge'] = ""
        
        pipeline_b2b = build_product_pipeline(bk_data, 'b2b_consult')
        fs['branches']['b2b_consult'] = [save_human_b2b] + pipeline_b2b + [qna_b2b] + rest_b2b

    with open(r'c:\Users\Administrator\Desktop\Hoc_python\VHN_DauTien_Fixed.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

process()
print("Success")
