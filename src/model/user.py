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
        result = DB.read_one(cls.collection, {'_id': user_id})
        if result.success:
            if result.message:
                return Result(success=True, message=cls(result.message))
            else:
                return Result(success=False, message="User not found", severity="WARNING")
        return result

    @classmethod
    def new(cls, user):
        return DB.create(cls.collection, user)
    