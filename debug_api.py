import requests
import json

try:
    # Try user_id 2 (Alice Johnson)
    response = requests.get("http://localhost:8000/api/subscriptions/?user_id=2")
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
