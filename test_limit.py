import os
import requests

API_KEY = "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"
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {"Authorization": f"Bearer {API_KEY}"}
payload = {
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "hello " * 2000}], # Send a large request
    "max_tokens": 4000
}

# Spam the API to hit the limit
for i in range(10):
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 429:
        print("429 Error:", response.json())
        break
    print(response.status_code)
