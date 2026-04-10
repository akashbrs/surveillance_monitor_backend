import requests

try:
    res = requests.post('http://127.0.0.1:8000/api/auth/google/', json={'token': 'test'})
    print("Status:", res.status_code)
    print("Response:", res.text)
except Exception as e:
    print("Error:", str(e))
