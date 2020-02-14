from flask import Flask
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config.from_envvar('APP_CONFIG_FILE')

print(app.debug)


@app.route('/')
def index():
    return "Coming soon"
