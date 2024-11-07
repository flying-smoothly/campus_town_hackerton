# Fourth: Lambda Function Processing
# File: lambda_function.py

import third_llamaindex_indexing as indexing
import json


def lambda_handler(event, context):
    # Event received from an API Gateway, assumed to include necessary restaurant data parameters
    index = indexing.create_restaurant_index()

    # Performing an action using the index, for example, fetching a restaurant review
    restaurant_name = event.get('restaurant_name')
    if restaurant_name:
        response = index.query(query=restaurant_name)
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }

    return {
        'statusCode': 400,
        'body': json.dumps("Invalid request")
    }

# Example test
# lambda_handler({'restaurant_name': '신머이쌀국수 숙대본점'}, None)