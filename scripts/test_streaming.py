import requests

url = "http://127.0.0.1:8000/ask-stream"
headers = {"X-API-Key": "Test", "Content-Type": "application/json"}
data = {"question": "What albums did Nas release in the 90s?", "session_id": "stream_test"}

response = requests.post(url, headers=headers, json=data, stream=True)

import time

for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
    print(f"[{time.time():.2f}] {chunk!r}")