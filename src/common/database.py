from pymongo import MongoClient, cursor
from src.common.result import Result

class DB:
    """ The mongo database API """
    db = []

    @classmethod
    def connect(cls, URL: str, env: str) -> Result:
        """
        Connects to the mongo database using the URL from environment 
        variables and the database from the environment. Returns a Result
        """
        try:
            cls.db = MongoClient(URL)[env]
        except Exception as e:
            return Result(success=False, message=str(e), severity='ERROR')
        return Result(success=True)

    @classmethod
    def create(cls, collection: str, record: str) -> Result:
        """
        Insert a new record into the passed collection and return a Result
        """
        try:
            message = cls.db[collection].insert_one(record).inserted_id
        except Exception as e:
            return Result(success=False, message=str(e), severity='WARNING')
        return Result(success=True, message=str(message))

    @classmethod
    def read(cls):
        pass

    @classmethod
    def update(cls):
        pass

    @classmethod
    def delete(cls):
        pass

    @classmethod
    def all(cls, collection: str) -> cursor:
        """
        Return a cursor pointing to all the records of the passed collection
        """
        return cls.db[collection].find()