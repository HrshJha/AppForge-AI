import os
import requests

API_KEY = "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"
url = "https://api.groq.com/openai/v1/models"
headers = {"Authorization": f"Bearer {API_KEY}"}
response = requests.get(url, headers=headers)
models = [m['id'] for m in response.json().get('data', [])]
print(models)
