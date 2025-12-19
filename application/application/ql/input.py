product = """
{{
  "id": {product_id},
  "similarProductsInput": {{
    "filter": {{
      "similarByProductId": {product_id}
    }},
    "page": {{
      "limit": 6,
      "page": 1
    }}
  }}
}}
"""

review = """
{{
  "input": {{
    "filter": {{"productId": {product_id}}}, 
    "page": {{}}
  }}
}}
"""