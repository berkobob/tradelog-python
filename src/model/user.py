from flask_login import UserMixin
from src.common.database import DB
from src.common.result import Result

class User(UserMixin):
    collection = 'user'

    def __init__(self, user):
        self.id = user['_id']
        self.email = user['email']
        self.name = user['name']
        self.profile_pic = user['profile_pic']


    @classmethod
    def get(cls, user_id):
        user = DB.read_one(cls.collection, {'_id': user_id})
        if user: return cls(user)

    @classmethod
    def new(cls, user):
        return DB.create(cls.collection, user)

    @classmethod
    def me(cls, email, name):
        result = DB.read_one(cls.collection, {'email': email, 'name': name})
        if not result.success: return result
        if not result.message: return Result(False, None, "WARNING")
        return Result(True, cls(result.message))
    