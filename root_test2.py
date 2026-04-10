import requests

try:
    res = requests.post('http://127.0.0.1:8000/api/auth/google/', json={'token': 'test'})
    print("Status:", res.status_code)
    with open('error_page.html', 'w') as f:
        f.write(res.text)
except Exception as e:
    print("Error:", str(e))
