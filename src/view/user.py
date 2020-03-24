from flask import Blueprint
from flask_login import login_user
from src.model.user import User

user = Blueprint('user', __name__)

@user.route('/login')
def login():
    login_user(User.get('105728265192260536412').message)
    return ('<p>You are now logged in</p>')

