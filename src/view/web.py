from flask import Blueprint, render_template, request, flash, redirect, redirect
from flask_login import current_user, login_required
from src.controller.tradelog import Log
import pygal

web = Blueprint('web', __name__)
reverse = False

@web.route('/')
def home():
    """ Render the home page """
    if current_user.is_authenticated:
        bar_chart = pygal.Bar()                                            # Then create a bar graph object
        bar_chart.add('Fibonacci', [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55])  # Add some values
        bar_chart.render_to_file('bar_chart.svg') 
        chart = bar_chart.render_data_uri()
        return render_template('home.html', ports=_ports(), chart=chart)
    else:
        return redirect('/user')

@web.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """ Create a new portfolio """
    if request.method == 'POST':

        result = Log.create_portfolio({
                    'name': request.form['name'],
                    'description': request.form['description']
                    })

        if result.success:
            flash (f'Portfolio {result.message.name} successfully created',
                'SUCCESS')
        else:
            flash (result.message, result.severity)

    return render_template('new.html')


@web.route('/load', methods=['GET', 'POST'])
@login_required
def load():
    """ select a file of raw trades to load and process """
    if request.method == 'GET': return render_template('load.html')

    f = request.files['file']
    try:
        f.save(f.filename)
    except Exception as e:
        flash(str(e), 'ERROR')
        return render_template('load.html')

    result = Log.load_trades_from(f.filename)

    if result.success:
        flash(f'{f.filename} loaded successfully! There are {result.message} new raw trades',
                'SUCCESS')
    else:
        flash(f'Failed to process {f.filename}. {result.message}', result.severity)   

    return render_template('load.html')


@web.route('/raw', methods=['GET', 'POST'])
@login_required
def commit():
    """ Convert a raw trade into a processed trade """
    global reverse
    sortby = request.args.get('sortby') if request.args.get('sortby') else 'TradeDate'

    if request.method == 'POST':
        result = Log.commit_raw_trade(request.form.get('raw_id'),
                                    request.form.get('port'))
        flash(result.message, result.severity)

    result=Log.get_raw_trades()

    if not result.success: 
        flash(result.message, result.severity)
        result.message = []
    trades = sorted(result.message, key = lambda i: i.trade[sortby], reverse=reverse)
    reverse = not reverse
    return render_template("raw_trades.html", trades=trades, ports=_ports())

@web.route('/port/<port>')
def port(port):
    """ List the stocks in this port """
    global reverse
    sortby = request.args.get('sortby') if request.args.get('sortby') else 'stock'

    result = Log.get_stocks(port)
    if not result.success:
        flash(result.message, result.severity)
        result.message = []
    
    stocks = sorted(result.message, key=lambda i: i[sortby], reverse=reverse)
    reverse = not reverse
    return render_template("stocks.html", port=port, stocks=stocks)

@web.route('/port/<port>/<stock>')
def stock(port, stock):
    """ List the positions in this stock in this port """
    open = Log.get_open_positions(port, stock)
    if not open.success: 
        flash(open.message, open.severity)
        open.message=[]
    if not open.message: flash("There are no open positions", "WARNING")
    closed = Log.get_closed_positions(port, stock)
    if not closed.success: 
        flash(closed.message, closed.severity)
        closed.message=[]
    if not closed.message: flash("There are no closed positions", "WARNING")
    return render_template("positions.html", open=open.message, closed=closed.message)

@web.route('/port/<port>/<stock>/open')
def open(port, stock):
    """ List the open positions and trades """
    return f"list open {stock} positions in {port}"

@web.route('/port/<port>/<stock>/closed')
def closed(port, stock):
    """ List closed positions and trades """
    result = Log.get_closed_positions(port=port, stock=stock)
    if not result.success:
        flash(result.message, result.severity)
        result.message = []
    return render_template('closed.html', closed=result.message)

@web.route('/position/<_id>')
def position(_id):
    result = Log.get_trades(_id)
    if not result.success: flash(result.message, result.severity)
    return render_template("trades.html", position=result.message)

@web.route('/logout')
def logout():
    return redirect('/user/logout')


# private functions

def _ports():
    result = Log.get_port_names()
    if not result.success:
        flash(result.message, result.severity)
        result.message = []
    if len(result.message) == 0:
        flash('There are no Portfolios. Create one before proceeding further', 
              'WARNING')
    ports = result.message
    return ports

