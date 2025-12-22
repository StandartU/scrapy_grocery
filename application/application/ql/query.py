product = """
query ProductFullData($id: Int!, $similarProductsInput: ProductsRequest!) {
  product(id: $id) {
    id
    code
    name

    images(includePromo: true) {
      id
    }

    price
    previousPrice

    description

    propertyValues {
      __typename
      property {
        name
        title
        unit
      }
      ... on StringPropertyValue {
        strValue
      }
      ... on ItemOfListPropertyValue {
        item {
          label
          value
        }
      }
    }

    rating
    numberOfRatings
  }
}
"""

review = """
query ($input: ProductReviewsRequest!) {
  productReviews(input: $input) {
    list {
      id
      grade
      text
      author
      adminResponse
      adminResponseDate
      dateCreated
    }
    page {
      total
    }
  }
}
"""

category = """
query ($input: ProductsRequest!) {
  products(input: $input) {
    list {
      id
    }
    page {
      total
      limit
      page
    }
  }
}
"""

