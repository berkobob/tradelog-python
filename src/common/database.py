from pymongo import MongoClient, cursor
from src.common.result import Result

class DB:
    """ The mongo database API """
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
    def read(cls, collection, query):
        try:
            message = cls.db[collection].find(query)
        except Exception as e:
            return Result(success=False, message=str(e), severity='ERROR')
        return Result(success=True, message=message)
        # if message: return Result(success=True, message=message)
        # return Result(success=False, message=f'No records found matching {query}', severity='WARNING')

    @classmethod
    def update(cls):
        pass

    @classmethod
    def delete(cls, collection, query):
        try:
            message = cls.db[collection].delete_one(query)
        except Exception as e:
            return Result(success=False, message=str(e), severity='ERROR')
        if message.deleted_count != 1:
            return Result(success=False, message='Failed to delete', severity='ERROR')
        return Result(success=True, message=message)

    # @classmethod
    # def all(cls, collection: str) -> cursor:
    #     """
    #     Return a cursor pointing to all the records of the passed collection
    #     """
    #     return cls.db[collection].find()