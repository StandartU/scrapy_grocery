import requests
from fake_useragent import UserAgent
from application.application.ql import input as i, query as q

ua = UserAgent().firefox

r = requests.post(
    "https://api.yarcheplus.ru/api/graphql",
    headers={"User-Agent": UserAgent().firefox,
             "token": "b31737583a88a1efbd5ea5118131fe710941cc82-3c542b74b41407360733197a8155c2dde3966c91"},
    json={
        "query": q.product,
        "variables": i.product.format(product_id=39452)
    }
)

print(r.text)
