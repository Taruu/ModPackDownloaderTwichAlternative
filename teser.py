import requests
headers = {
    'User-Agent': 'My User Agent 1.0',
    'From': 'youremail@domain.com',  # This is another valid field
}
response = requests.get('https://addons-ecs.forgesvc.net/api/v2/addon/228404',headers=headers)

print(response.status_code)
print(response.headers)
print(response.text)

response = requests.get("https://addons-ecs.forgesvc.net/api/v2/addon/223008/file/2828357/download-url",headers=headers)
print(response.status_code)
print(response.content)
headers = {
    'User-Agent': 'My User Agent 1.0',
    'From': 'youremail@domain.com',  # This is another valid field
    "If-None-Match" : '"1da9dd8478ba6d682f2787746776e18a"'
}
mod_download_text = requests.get("https://addons-ecs.forgesvc.net/api/v2/addon/223008/file/2828357/download-url", headers=headers)
mod_download = requests.get(mod_download_text.text, headers=headers)
print(mod_download.headers)
print(mod_download.status_code)
with open(mod_download_text.text.split("/")[-1], 'wb') as ModFile:
    for i, chunk in enumerate(mod_download.iter_content(chunk_size=1024)):
        ModFile.write(chunk)
        ModFile.flush()
    ModFile.close()