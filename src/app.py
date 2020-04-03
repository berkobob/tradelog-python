from os import environ, urandom
from flask import Flask
from src.view.web import web
from src.view.user import user
from src.common.database import DB
from src.model.user import User
from flask_login import LoginManager
from datetime import datetime
import sys

app = Flask(__name__)
app.register_blueprint(web)
app.register_blueprint(user, url_prefix='/user')

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

try:
    app.config.from_object('config.'+app.config['ENV'])
except:
    app.config['DB_URL'] = environ.get('DB_URL')
    app.config['SECRET_KEY'] = urandom(24)
    app.config['GOOGLE_CLIENT_ID'] = environ.get('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = environ.get('GOOGLE_CLIENT_SECRET')
    app.config['GOOGLE_DISCOVERY_URL'] = environ.get('GOOGLE_DISCOVERY_URL')

try:
    DB.connect(app.config['DB_URL'], app.config['ENV'])
except Exception as e:
    print('Failed to connect to database\n', e)
3    sys.exit()
else:
    print(f" * Succesfully connected to the {app.config['ENV']} database *")


@app.template_filter('ftime')
def _format_date(date):
    try:
        return datetime.strftime(date, "%d/%m/%Y")
    except:
        return " "

@app.template_filter('ffloat')
def _format_float(num):
    # return '{:{width}.{prec}f}'.format(num, width=5, prec=2)
    if num: return '${:,.2f}'.format(num)
    return ""