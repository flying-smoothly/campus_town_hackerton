# Third: LlamaIndex Indexing
# File: third_llamaindex_indexing.py

import llamaindex
import json

def create_restaurant_index():
    # Load restaurant reviews data
    with open("restaurant_reviews.json", "r", encoding="utf-8") as json_file:
        reviews_data = json.load(json_file)

    # Create index using LlamaIndex
    index = llamaindex.Index()
    for review in reviews_data:
        index.add_document(
            doc_id=review['name'],
            text=json.dumps(review)
        )
    return index

# Generate index
# create_restaurant_index()
