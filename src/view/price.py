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
    result = Log.price()
    if not result.success:
        flash(result.message, 'ERROR')
        return redirect(request.referrer)
    return render_template('port_prices.html', ports=result.message)

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
    prices = sorted(Price.get_price(open.message), key=lambda i: i[sortby], reverse=reverse)
    reverse = not reverse
    return render_template('prices.html', prices=prices, port=port)
