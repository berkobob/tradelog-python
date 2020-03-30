from pymongo import MongoClient, cursor
from src.common.result import Result
from src.common.exception import AppError

class DB:
    """ 
    The mongo database API 
    Should only deal with database errors and not application errors
    """
    db = []
    # return Result(success=False, message='Panic!', severity='ERROR')

    @classmethod
    def connect(cls, URL: str, env: str) -> Result:
        """
        Connects to the mongo database using the URL from environment 
        variables and the database from the environment. Returns a Result
        """
        try:
            cls.db = MongoClient(URL, connectTimeoutMS=30000, 
                                socketTimeoutMS=None, socketKeepAlive=True, 
                                connect=False, maxPoolsize=1)[env]
        except Exception as e:
            raise AppError(e, 'ERROR')

    @classmethod
    def create(cls, collection: str, record: str) -> Result:
        """
        Insert a new record into the passed collection and return a Result
        """
        try:
            result = cls.db[collection].insert_one(record)
        except Exception as e:
            raise AppError(e)
        else:
            return result

    @classmethod
    def read_one(cls, collection: str, query: dict):
        try:
            document = cls.db[collection].find_one(query)
        except Exception as e:
            return AppError(e)
        else:
            return document

    @classmethod
    def read_many(cls, collection, query):
        try:
            documents = cls.db[collection].find(query)
        except Exception as e:
            raise AppError(e)
        else:
            return documents

    @classmethod
    def update(cls, collection, query, values):
        try:
            result = cls.db[collection].update(query, values)
        except Exception as e:
            raise AppError(e)
        else:
            return result

    @classmethod
    def delete(cls, collection, query):
        try:
            result = cls.db[collection].delete_one(query)
        except Exception as e:
            raise AppError(e)
        else: 
            return result
