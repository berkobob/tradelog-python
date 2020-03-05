from pymongo import MongoClient

client = MongoClient('mongodb+srv://tradelog:tradelog@cluster0-4ov7h.mongodb.net/test?retryWrites=true&w=majority')
db = client.test
raw = db.raw
print(raw.find_one())

for trade in raw.find():
    print(trade)