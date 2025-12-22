import requests
from fake_useragent import UserAgent
from application.application.ql import payload as p

ua = UserAgent().firefox

r = requests.post(
    "https://api.yarcheplus.ru/api/graphql",
    headers={"User-Agent": UserAgent().firefox,
             "token": "9d4507a662a277a1f073f0b139e5fb6ba1684719-38b62eadc243542dca1f49d83c6cf794f1aaf840"},
    json=p.get_category_payload(732)
)

print(r.text)
print(len(r.json()["data"]["products"]["list"]))
