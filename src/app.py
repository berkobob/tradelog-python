from os import environ, urandom
from flask import Flask, current_app
from src.model.mongodb import DB
from src.controller.web import web

app = Flask(__name__, template_folder='view')
app.register_blueprint(web)

try:
    app.config.from_object('config.'+app.config['ENV'])
except:
    app.config['DB_URL'] = environ.get('DB_URL')
    app.config['SECRET_KEY'] = urandom(24)

DB.connect(app.config['DB_URL'], app.config['ENV'])
