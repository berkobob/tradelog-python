import os
from flask import Flask

app = Flask(__name__)
app.config.from_object('config.'+app.config['ENV'])

@app.route('/')
def index():
    return "Coming soon"
