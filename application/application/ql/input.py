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

category = """
{{
  "variables": {{
    "input": {{
      "page": {{
        "page": 1,
        "limit": 48
      }},
      "sort": {{
        "param": "default",
        "direct": "asc"
      }},
      "filter": {{
        "byCategoryIds": [
          {category_id}
        ]
      }}
    }}
  }}
}}
"""