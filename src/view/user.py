from flask import Blueprint, current_app, render_template, flash, url_for
from flask import redirect, request
from flask_login import login_user, logout_user
from src.view.web import web
from oauthlib.oauth2 import WebApplicationClient
import requests, json
from passlib.hash import sha256_crypt as crypt 

user = Blueprint('user', __name__)
client = None

@user.route('/login', methods=['GET', 'POST'])
def hold():
    if request.method == 'GET': return render_template('login.html')

    email = request.form['email']
    password = request.form['password']
    user = User.get(email)
    if user and crypt.verify(password, user.password):
        login_user(user)
        flash (f'Login successful. Welcome back {user.name}', 'SUCCESS')
        return redirect(url_for(web.home))

    flash('Invalid credentials! You are not logged in.', 'WARNING')
    return render_template('login.html')

@user.route('/google_login')
def login():
    global client
    DISCO_URL = current_app.config['GOOGLE_DISCOVERY_URL']
    CLIENT = current_app.config['GOOGLE_CLIENT_ID']
    client = WebApplicationClient(CLIENT)

    google_provider_cfg = requests.get(DISCO_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
        )
    return redirect(request_uri)

@user.route('/login/callback')
def callback():
    global client

    config = requests.get(current_app.config['GOOGLE_DISCOVERY_URL']).json()

    token_url, headers, body = client.prepare_token_request(
        config['token_endpoint'],
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=request.args.get('code')
        )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(current_app.config['GOOGLE_CLIENT_ID'], 
              current_app.config['GOOGLE_CLIENT_SECRET']),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = config["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get('email_verified'):
        unique_id = userinfo_response.json()["sub"]
        # users_email = userinfo_response.json()["email"]
        # picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    user = User.get(unique_id)
    if user and login_user(user):
        flash (f'Logon successful. Welcome back {users_name}', 'SUCCESS')
        return redirect('/')
    else: 
        flash('Invalid credentials! You are not logged in.', 'WARNING')
        flash(f'Could not get user with ID {unique_id} from {User.collection}')
        return render_template('login.html')

@user.route('/logout')
def logout():
    logout_user()
    return render_template("login.html")

   

"""
from passlib.hash import sha256_crypt

password = sha256_crypt.encrypt("password")
password2 = sha256_crypt.encrypt("password")

print(password)
print(password2)

print(sha256_crypt.verify("password", password))
		
https://pythonprogramming.net/password-hashing-flask-tutorial/
"""
