from flask import Blueprint, render_template, request, flash, redirect
from src.controller.tradelog import Log

web = Blueprint('web', __name__)
reverse = False

@web.route('/')
def home():
    """ Render the home page """
    return render_template('home.html', ports=_ports())

@web.route('/new', methods=['GET', 'POST'])
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

    return render_template('new.html', ports=_ports())


@web.route('/load', methods=['GET', 'POST'])
def load():
    """ select a file of raw trades to load and process """
    if request.method == 'GET': return render_template('load.html', ports=_ports())

    f = request.files['file']
    try:
        f.save(f.filename)
    except Exception as e:
        flash(str(e), 'ERROR')
        return render_template('load.html', ports=_ports())

    result = Log.load_trades_from(f.filename)

    if result.success:
        flash(f'{f.filename} loaded successfully! There are {result.message} new raw trades',
                'SUCCESS')
    else:
        flash(f'failed to process {f.filename}', result.severity)   

    return render_template('load.html', ports=_ports())


@web.route('/raw', methods=['GET', 'POST'])
def commit():
    """ Convert a raw trade into a processed trade """
    if request.method == 'GET':
        result=Log.get_raw_trades()
        if not result.success:
            flash(result.message, result.severity)
            return render_template("base.html")

        trades = sorted(result.message, key = lambda i: i.trade['TradeDate'])
        return render_template("raw_trades.html", trades=trades, ports=_ports())

    # POST
    result = Log.commit_raw_trade(request.form.get('raw_id'),
                                  request.form.get('port'))
    flash(result.message, result.severity)

    result = Log.get_raw_trades()
    if not result.success: flash(result.message, result.severity)
    trades = sorted(result.message, key = lambda i: i.trade['TradeDate'])
    return render_template('raw_trades.html', ports=_ports(), trades=trades)


@web.route('/raw/<col>')
def raw(col):
    global reverse
    trades = sorted(Log.get_raw_trades().message, 
                    key=lambda i: i.trade[col],
                    reverse=reverse)
    reverse = not reverse
    return render_template("raw_trades.html", trades=trades, ports=_ports())

@web.route('/raw/<first>/<second>')
def raw2(first, second):
    global reverse
    col = f"{first}/{second}"
    trades = sorted(Log.get_raw_trades().message, 
                    key=lambda i: i.trade[col],
                    reverse=reverse)
    reverse = not reverse
    return render_template("raw_trades.html", trades=trades, ports=_ports())

@web.route('/port/<name>')
def port(name):
    result = Log.get_stocks(name)
    if result.success: return str(result.message)
    else: flash(result.message, result.severity)
    return f"Portfolio: {name}"


""" Private Functions """

def _ports():
    result = Log.get_port_names()
    if len(result.message) == 0:
        flash('There are no Portfolios. Create one before proceeding further', 
              'WARNING')
    if not result.success:
        flash(result.message, result.severity)
        result.message = []
    return result.message