from pymongo import MongoClient, cursor
from src.common.result import Result

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
            return Result(success=False, message=str(e), severity='ERROR')
        return Result(success=True, message=cls.db, severity='SUCCESS')

    @classmethod
    def create(cls, collection: str, record: str) -> Result:
        """
        Insert a new record into the passed collection and return a Result
        """
        try:
            message = cls.db[collection].insert_one(record)
        except Exception as e:
            return Result(success=False, message=str(e), severity='WARNING')
        return Result(success=True, message=str(message), severity='SUCCESS')

    @classmethod
    def read_one(cls, collection: str, query: dict):
        try:
            message = cls.db[collection].find_one(query)
        except Exception as e:
            return Result(success=False, message=str(e), severity='ERROR')
        return Result(success=True, message=message, severity='SUCCESS')

    @classmethod
    def read_many(cls, collection, query):
        try:
            message = cls.db[collection].find(query)
        except Exception as e:
            return Result(success=False, message=str(e), severity='ERROR')
        return Result(success=True, message=message, severity='SUCCESS')

    @classmethod
    def update(cls, collection, query, values):
        try:
            message = cls.db[collection].update(query, values)
        except Exception as e:
            return Result(success=False, message=str(e), severity='ERROR')
        return Result(success=True, message=message, severity='SUCCESS')

    @classmethod
    def delete(cls, collection, query):
        try:
            message = cls.db[collection].delete_one(query)
        except Exception as e:
            return Result(success=False, message=str(e), severity='ERROR')
        return Result(success=True, message=message, severity='SUCCESS')
