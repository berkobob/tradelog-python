from os import environ, urandom
from flask import Flask
from src.view.web import web
from src.controller.tradelog import init

app = Flask(__name__)
app.register_blueprint(web)

try:
    app.config.from_object('config.'+app.config['ENV'])
except:
    pass

if 'DB_URL' not in app.config.keys():
    app.config['DB_URL'] = environ.get('DB_URL')

if app.config['SECRET_KEY'] is None:
    app.config['SECRET_KEY'] = urandom(24)

init(app.config['DB_URL'], app.config['ENV'])