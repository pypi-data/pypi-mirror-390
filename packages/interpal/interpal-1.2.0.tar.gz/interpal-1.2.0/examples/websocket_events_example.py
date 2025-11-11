import requests

proxies = {
    'http': 'http://localhost:9495/',
    'https': 'http://localhost:9495/',
}

# cookies = {
#     '__ubic1': 'NjAwNTY3OTU2NjkwODgxYjIzYjg3ZDAuNzQzOTYzNjY%3D',
#     'interpals_sessid': 'a4kfjkajno6ptnu3mqtbi4qmoa',
# }

headers = {
    'Host': 'api.interpals.net',
    'Accept': '/',
    'baggage': 'sentry-environment=production,sentry-public_key=2f014b58daae4f2fa87f9772d0a5c050,sentry-trace_id=9563e55d8c9e4788abda2ac72c3e82a8',
    'Accept-Language': 'en-US',
    'sentry-trace': '9563e55d8c9e4788abda2ac72c3e82a8-af349f9f5b63c7d3',
    'User-Agent': 'InterPals/324 CFNetwork/3860.100.1 Darwin/25.0.0',
    'x-device-id': '034E7E7C-F6B0-400C-89FD-31FA229DC50A',
    'x-auth-token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC9hcGkuaW50ZXJwYWxzLm5ldFwvIiwiYXVkIjoiaHR0cDpcL1wvYXBpLmludGVycGFscy5uZXRcLyIsImlhdCI6MTc2MjQ5ODY4NSwibmJmIjoxNzYyNDk4Njg1LCJleHAiOjE3NzAyNzQ2ODUsInVpZCI6IjE0NDY0MzM4OTY5NTcyOTYwMzgiLCJqdGkiOiIxODMzNDI1NDI3Njk2Njg2MTcwIn0.XvcDH9jWfqil2_bTSoTQANmtH0wkjebkn_6CCNCxcC4',
    'x-app-version': 'ios-2.4.3',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': '__ubic1=NjAwNTY3OTU2NjkwODgxYjIzYjg3ZDAuNzQzOTYzNjY%3D; interpals_sessid=a4kfjkajno6ptnu3mqtbi4qmoa',
}

data = {
    'thread_id': '1833435079742223361',
    'attachment_type': 'gif',
    'tmp_id': '34bc',
    'gif_attachment_url': 'https://media3.giphy.com/media/v1.Y2lkPTU4YWY4YzA5a2Rldmp6NTZ2c2RhN21seGp1NjVyZGQ1czJna21qZmxqcWI4eG0zaCZlcD12MV9naWZzX3RyZW5kaW5nJmN0PWc/YOuRCwUvMTQRX3TA7s/giphy-preview.gif',
}

response = requests.post('https://api.interpals.net/v1/message', headers=headers, data=data)
print(response.json())