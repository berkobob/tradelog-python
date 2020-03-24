from flask import Blueprint, render_template, request, flash, redirect
from flask_login import current_user, login_required
from src.controller.tradelog import Log

web = Blueprint('web', __name__)
reverse = False

@web.route('/')
def home():
    """ Render the home page """
    if current_user.is_authenticated:
        return render_template('home.html', ports=_ports())
    else:
        return "<h1> Login dummy</h1>"

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
        flash(f'failed to process {f.filename}', result.severity)   

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
    if not result.success: flash(result.message, result.severity)
    trades = sorted(result.message, key = lambda i: i.trade[sortby], reverse=reverse)
    reverse = not reverse
    return render_template("raw_trades.html", trades=trades, ports=_ports())

@web.route('/port/<port>')
def port(port):
    """ List the stocks in this port """
    result = Log.get_stocks(port)
    if not result.success: flash(result.message, result.severity)
    return render_template("stocks.html", stocks=result.message)

@web.route('/port/<port>/<stock>')
def stock(port, stock):
    """ List the positions in this stock in this port """
    result = Log.get_positions(port, stock)
    if not result.success: flash(result.message, result.severity)
    return render_template("positions.html", open=result.message[0], closed=result.message[1])

@web.route('/port/<port>/<stock>/open')
def open(port, stock):
    """ List the open positions and trades """
    return f"list open {stock} positions in {port}"

@web.route('/port/<port>/<stock>/closed')
def closed(port, stock):
    """ List closed positions and trades """
    return f"list closed {stock} positions in {port}"


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