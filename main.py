import requests
from fake_useragent import UserAgent
from ql import input as i
from ql import query as q

ua = UserAgent().firefox

r = requests.post(
    "https://api.yarcheplus.ru/api/graphql",
    headers={"User-Agent": UserAgent().firefox,
             "token": "a6a559f905e0966210d2c54fe0c3d2f1fc7951f1-a529f6ea78dbe1eeff39c1034e8f11fe6c33aad4"},
    json={
        "query": q.product,
        "variables": i.product.format(product_id=39480)
    }
)

print(r.text)
