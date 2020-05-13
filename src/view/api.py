import operator
from flask import Blueprint, jsonify, abort
from src.controller.tradelog import Log

api = Blueprint('api', __name__)

@api.route('/')
def home():
    ports = Log.get_ports()
    if not ports.success:
        abort(500, ports.message)
    return jsonify([port.to_json() for port in ports.message])
    # return [vars(port) for port in ports.message].toString()
    # return ports.message[0].to_json()

@api.route('/port/<port>')
def port(port):
    result = Log.get_stocks(port)
    if not result.success:
        abort(500, result.message)

    result.message.sort(key=operator.attrgetter('stock'))
    return jsonify([stock.to_json() for stock in result.message])

@api.route('/positions/<port>/<stock>')
def positions(port, stock):
    result = Log.get_positions(port, stock)
    if not result.success:
        abort(500, result.message)

    result.message.sort(key=operator.attrgetter('open'), reverse=True)
    return jsonify([position.to_json() for position in result.message])

@api.route('/trades/<id>')
def trades(id):
    result = Log.get_trades(id)
    if not result.success:
        abort(500, result.message)

    return jsonify([trade.to_json() for trade in result.message])