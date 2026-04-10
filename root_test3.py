import requests
try:
    res = requests.get('http://127.0.0.1:8000/admin/')
    print("Admin Status:", res.status_code)
except Exception as e:
    print("Error:", str(e))
