from flask import Blueprint, render_template, request, flash, redirect
from src.controller.tradelog import create_portfolio, get_port_names, load_trades_from, get_raw_trades, commit_raw_trade

web = Blueprint('web', __name__)

@web.route('/')
def home():
    """ Render the home page """
    return render_template('home.html', ports=_ports())

@web.route('/new', methods=['GET', 'POST'])
def new():
    """ Create a new portfolio """
    if request.method == 'POST':
        port = {'name': request.form['name'],
                'description': request.form['description']}

        result = create_portfolio(port)

        if result.success:
            flash (f'Portfolio {port["name"]} successfully created', 'SUCCESS')
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

    result = load_trades_from(f.filename)

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
        result=get_raw_trades()
        if not result.success:
            flash(result.message, result.severity)
            result.message = []
            return render_template("base.html")

        return render_template("raw_trades.html", trades=result.message, ports=_ports())


    result = commit_raw_trade(request.form.get('raw_id'), request.form.get('port'))
    
    if result.success: 
        flash('Trade committed', 'SUCCESS')
        print(result.message)
    else: flash(result.message, result.severity)

    # Because this page uses the .csv header row as a table header, when there
    # are no more trades to commit we can't show an empty table because we can't
    # show any headers so send home with flash message

    trades = get_raw_trades().message

    return render_template('raw_trades.html', ports=_ports(), trades=trades)


""" Private Functions """

def _ports():
    result = get_port_names()
    if len(result.message) == 0:
        flash('There are no Portfolios. Create one before proceeding further', 'WARNING')
    if not result.success:
        flash(result.message, result.severity)
        result.message = []
    return result.message