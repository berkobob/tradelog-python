from flask_login import UserMixin
from flask import current_app
from src.common.database import DB
from src.common.result import Result

class User(UserMixin):
    collection = 'users'

    def __init__(self, user):
        self.id = user['_id']
        self.email = user['email']
        self.name = user['name']
        self.profile_pic = user['profile_pic']

    def is_admin(self):
        return self.name == current_app.config['ADMIN']

    @classmethod
    def get(cls, user_id):
        user = DB.read_one(cls.collection, {'_id': user_id})
        if user: return cls(user)

    @classmethod
    def new(cls, user):
        return DB.create(cls.collection, user)

    @classmethod
    def me(cls, email, name):
        user = DB.read_one(cls.collection, {'email': email, 'name': name})
        if user: return cls(user)
        return None

    @classmethod
    def create(cls, user):
        """ Save a copy of the class in the DB, add the _id and return the object """
        return DB.create(cls.collection, user)
    