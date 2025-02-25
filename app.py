import requests

API_URL = "https://checkvisaslots.com/pro.html#api_key_info"
API_KEY = "N8724G"

def fetch_latest_screenshot():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(API_URL, headers=headers)
        
        # ✅ Check if response is empty or invalid
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return None  # Prevent script from crashing
        
        try:
            data = response.json()
            return data
        except requests.exceptions.JSONDecodeError:
            print("❌ Error: API returned invalid JSON.")
            return None
        
    except requests.RequestException as e:
        print(f"❌ Network Error: {e}")
        return None
