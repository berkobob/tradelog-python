from os import environ, urandom
from flask import Flask
from src.view.web import web
from src.view.user import user
from src.common.database import DB
from src.model.user import User
from flask_login import LoginManager

app = Flask(__name__)
app.register_blueprint(web)
app.register_blueprint(user, url_prefix='/user')

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id).message

try:
    app.config.from_object('config.'+app.config['ENV'])
except:
    pass

if 'DB_URL' not in app.config.keys():
    app.config['DB_URL'] = environ.get('DB_URL')

if app.config['SECRET_KEY'] is None:
    app.config['SECRET_KEY'] = urandom(24)

result = DB.connect(app.config['DB_URL'], app.config['ENV'])

if not result.success:
    print ("*** FATAL ERROR. Cannot connect to database ***")
    print(result.message)
    exit()
else: print(f" * Succesfully connected to the {app.config['ENV']} database *")
