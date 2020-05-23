import operator
from flask import Blueprint, render_template, redirect, request, flash
from flask_login import login_required
from src.model.price import Price
from src.controller.tradelog import TradeLog as Log

price = Blueprint('price', __name__)
reverse = False

@price.route('/')
@login_required
def prices_root():
    return render_template('port_prices.html', ports=_prices(Log.get_ports().message))

@price.route('/stocks')
@login_required
def stocks():
    global reverse
    sortby = request.args.get('sortby') if request.args.get('sortby') else "_id"
    prices = Log.prices()
    prices.sort(key=operator.attrgetter(sortby), reverse=reverse)
    reverse = not reverse
    return render_template('update.html', prices=prices)

@price.route('/stocks/<stock>/<symbol>')
@login_required
def yahoo(stock, symbol):
    print(stock, symbol)
    Price.get(stock).update({'yahoo': symbol})
    return render_template('update.html', prices=Log.prices())

@price.route('/update')
@login_required
def update():
    Log.update()
    return redirect(request.referrer)

@price.route('/delete/<stock>')
@login_required
def delete(stock):
    Log.delete_price(stock)
    return render_template('update.html', prices=Log.prices())

@price.route('/port/<port>')
@login_required
def prices(port):
    global reverse
    open = Log.get_open_positions(port, None)

    if not open.success: 
        flash(open.message, open.severity)
        return redirect('/price')
    if not open.message: flash("This portfolio contains no open positions", "WARNING")
    
    sortby = request.args.get('sortby') if request.args.get('sortby') else 'stock'
    prices = sorted(_price(open.message), key=lambda i: i[sortby], reverse=reverse)
    reverse = not reverse
    return render_template('prices.html', prices=prices, port=port)

def _price(positions):
    prices = Price.read({}, True)
    message = []

    for position in positions:
        if 'shares' in position.position:
            _prices = [price.price for price in prices if price._id == position.stock]
            if len(_prices) == 0: price = 0
            else: price = _prices[0]
            percent = (price-position.risk_per) / position.risk_per if position.risk_per != 0 else 0
            message.append({
                'stock': position.stock,
                'cost': position.risk_per,
                'price': price,
                'percent': percent,
                'value': price * position.quantity
            })

    return message

def _prices(ports):
    message = []
    for port in ports:
        positions = [position for position in Log.get_open_positions(port.name).message]
        message.append({
            'port': port.name,
            'value': sum(price['value'] for price in _price(positions))
        })
    return message