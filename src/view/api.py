from flask import Blueprint, jsonify, abort
from src.controller.tradelog import Log

api = Blueprint('api', __name__)

@api.route('/')
def home():
    ports = Log.get_ports()
    if not ports.success:
        abort(500, ports.message)
    return jsonify([port.to_json() for port in ports.message])
