import requests

url = "http://10.0.2.101:1443/post_position"

payload={}
headers = {}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
