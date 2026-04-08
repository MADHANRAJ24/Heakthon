import requests
import json

try:
    response = requests.post("http://127.0.0.1:8000/reset", json={"task_id": "easy"})
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
