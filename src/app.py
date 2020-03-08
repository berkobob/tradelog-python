from model.mongodb import DB
from flask import Flask
from controller.web import web

app = Flask(__name__, template_folder='view')
app.register_blueprint(web)

try:
    app.config.from_object('config.'+app.config['ENV'])
except:
    pass

db = DB(app.config['DB_URL'], app.config['ENV'])
