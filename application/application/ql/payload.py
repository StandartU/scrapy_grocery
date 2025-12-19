from ..ql import query as q

def get_product_payload(product_id: str) -> dict:
    return {
        "query": q.product,
        "variables": {
            "id": int(product_id),
            "similarProductsInput": {
                "filter": {
                    "similarByProductId": int(product_id)
                },
                "page": {
                    "limit": 6,
                    "page": 1
                }
            }
        }
    }

def get_review_payload(product_id: str) -> dict:
    return {
        "query": q.review,
        "variables": {
            "input": {
                "filter": {
                    "productId": int(product_id)
                },
                "page": {}
            }
        }
    }