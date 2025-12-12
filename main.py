import requests
from fake_useragent import UserAgent

r = requests.get("https://5ka.ru/", headers={"User-Agent": UserAgent().firefox})

print(r.text)