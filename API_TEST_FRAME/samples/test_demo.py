import requests


urls = 'http://127.0.0.1:3000/api/register'
post_data = '{"email":"sydney@fife"}'

res = requests.post(
                url = urls,
                headers = {"Content-Type": "application/json;charset=UTF-8;multipart/form-data"},
                params = None,
                json = post_data,
                timeout=10 )
print(res.json())