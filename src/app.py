import os
from flask import Flask

app = Flask(__name__)
app.config.from_object('config.'+app.config['ENV'])

print('*** ENV ***', app.config['ENV'])
print('** TEST **', app.config['TESTING'])
print('* DEBUG *', app.config['DEBUG'])


@app.route('/')
def index():
    return "Coming soon"
