from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv('.env.test')
print(os.getenv('NAME'))

# print(os.environ)

# for value in os.environ:
#     print(value, ':\t', os.getenv(value))

