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

def get_category_payload(category_id: int, page: int = 1, limit: int = 48) -> dict:
    return {
        "query": q.category,
        "variables": {
            "input": {
                "page": {
                    "page": int(page),
                    "limit": int(limit)
                },
                "sort": {
                    "param": "default",
                    "direct": "asc"
                },
                "filter": {
                    "byCategoryIds": [int(category_id)]
                }
            }
        }
    }