import pymongo

client = pymongo.MongoClient()
db = client['some_db']
collection = db["some_collection"]

collection.insert({"textfield": "cool stuff in a doc"})
collection.create_index([('textfield', 'text')])

search_this_string = "stuff"
print collection.find({"$text": {"$search": search_this_string}}).count()
