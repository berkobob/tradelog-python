from pymongo import MongoClient, cursor
from src.common.exception import AppError

class DB:
    """ 
    The mongo database API 
    Should only deal with database errors and not application errors
    """

    @classmethod
    def connect(cls, URL: str, env: str):
        """
        Connects to the mongo database using the URL from environment
        variables and the database from the environment.
        """
        try:
            cls.client = MongoClient(URL, connectTimeoutMS=30000, 
                                socketTimeoutMS=None, socketKeepAlive=True, 
                                connect=False, maxPoolsize=1)
        except Exception as e:
            raise AppError(e, 'ERROR')
        else:
            cls.name = env
            cls.db = cls.client[env]
            return cls.client.admin.command('ping')

    @classmethod
    def create(cls, collection: str, record: str):
        """
        Insert a new record into the passed collection
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
            raise AppError("DB.read_many: "+str(e))
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

    @classmethod
    def ping(cls):
        try:
            result = cls.client.admin.command('ping')
        except Exception as e:
            raise AppError(e)
        else:
            return result

    @classmethod
    def drop(cls):
        try:
            cls.client.drop_database(cls.name)
        except Exception as e:
            raise AppError(e)
        else:
            return True