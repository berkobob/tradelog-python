from flask import Blueprint, current_app
from flask import redirect, request
from flask_login import login_user, logout_user
from src.model.user import User
from oauthlib.oauth2 import WebApplicationClient
import requests, json

user = Blueprint('user', __name__)
client = None

@user.route('/')
def hold():
    return('<a href="/user/login">Login</a>')

@user.route('/login')
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
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    result = User.get(unique_id)
    if result.success:
        login_user(result.message)
        return redirect('/')

    return "Invalid login credentials"

@user.route('/logout')
def logout():
    logout_user()
    return("<p>You are logged out</p>")

@user.route('/me')
def temp():
    email = request.args.get('email')
    name = request.args.get('name')
    result = User.me(email, name)
    if result.success:
        if result.message:
            login_user(result.message)
            return "You're logged in ", result.message.name
    return "Invalid credentials"

