import urllib.request
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

url = "https://hook.us2.make.com/d5qjovk3krdn0s21x8g55g124b42319m"

def test_api(payload):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            resp_body = response.read().decode('utf-8')
            print("Status:", response.status)
            try:
                print(json.dumps(json.loads(resp_body), indent=2, ensure_ascii=False)[:1000])
            except:
                print("Not JSON:", resp_body[:500])
    except Exception as e:
        print("Error:", e)

payload = {
    "bot_uuid": "test",
    "channel_type": "test",
    "channel_id": "test",
    "thread_id": "test",
    "user_msg_id": "test",
    "vendor": ["christina"],
    "product_type": ["cream"],
    "sheet_url":"https://docs.google.com/spreadsheets/d/1LdO_BV7DHdgs0_GAqTTkQbWkwefUQqw036Cb3PJcUJM/edit?usp=sharing"
}

print("Testing API with array...")
test_api(payload)

print("\nTesting API with string...")
payload["vendor"] = "christina"
payload["product_type"] = "cream"
test_api(payload)
