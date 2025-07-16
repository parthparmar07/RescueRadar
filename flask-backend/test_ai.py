import requests
import json

# Test the AI analysis endpoint
url = "http://localhost:5000/api/ai-analysis"
data = {
    "description": "injured dog needs immediate help, bleeding from leg",
    "location": "central park"
}

try:
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("Error:", str(e))
