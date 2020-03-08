from os import environ, urandom
from flask import Flask, current_app
from src.model.mongodb import DB
from src.controller.web import web

app = Flask(__name__, template_folder='view')
app.register_blueprint(web)

try:
    app.config.from_object('config.'+app.config['ENV'])
except:
    pass

if 'DB_URL' not in app.config.keys():
    app.config['DB_URL'] = environ.get('DB_URL')

if app.config['SECRET_KEY'] is None:
    app.config['SECRET_KEY'] = urandom(24)

print('DB_URL:', app.config['DB_URL'])
print('SECRET_KEY', app.config['SECRET_KEY'])

DB.connect(app.config['DB_URL'], app.config['ENV'])
