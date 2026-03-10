import requests
import json

def test_chat():
    url = "http://127.0.0.1:8000/chat"
    payload = {
        "session_id": "test_123",
        "message": "Hola, ¿quién eres y qué puedes hacer?"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_health():
    url = "http://127.0.0.1:8000/health"
    try:
        response = requests.get(url)
        print(f"Health Status: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Note: Require the server running in another terminal 'python main.py'
    print("Testing Health API...")
    test_health()
    print("\nTesting Chat API...")
    test_chat()
