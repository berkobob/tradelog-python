from flask_login import UserMixin
from flask import current_app
from src.common.database import DB
from src.common.result import Result
from src.model.model import Model

class User(UserMixin, Model):
    collection = 'users'

    def __init__(self, user):
        self.id = user['_id']
        self.email = user['email']
        self.name = user['name']
        self.password = user['password']

    def is_admin(self):
        return self.name == current_app.config['ADMIN']

    @classmethod
    def new(cls, user):
        return DB.create(cls.collection, user)

    @classmethod
    def create(cls, user):
        """ Save a copy of the class in the DB, add the _id and return the object """
        return DB.create(cls.collection, user)
    