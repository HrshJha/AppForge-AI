import os
import requests

API_KEY = "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"
url = "https://api.groq.com/openai/v1/models"
headers = {"Authorization": f"Bearer {API_KEY}"}
response = requests.get(url, headers=headers)
models = [m['id'] for m in response.json().get('data', [])]
print(models)
