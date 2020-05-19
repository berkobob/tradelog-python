from flask import Blueprint, render_template, request, flash, redirect, redirect
from flask_login import current_user, login_required
from src.controller.tradelog import TradeLog as Log 
from src.controller.prices import Prices
import pygal, operator

web = Blueprint('web', __name__)
reverse = False

@web.route('/')
def home():
    """ Render the home page """
    if current_user.is_authenticated:
        # bar_chart = pygal.Bar()                                            # Then create a bar graph object
        # bar_chart.add('Fibonacci', [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55])  # Add some values
        # bar_chart.render_to_file('bar_chart.svg') 
        # chart = bar_chart.render_data_uri()
        sortby = request.args.get('sortby')
        return render_template('home.html', ports=_sort(_ports(), sortby), chart=None)
    else:
        return redirect('/user')

@web.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """ Create a new portfolio """
    if request.method == 'POST':

        result = Log.create_portfolio({
                    'name': request.form['name'],
                    'description': request.form['description'],
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
    if request.method == 'GET': return render_template('load.html', action='/load')

    f = request.files['file']
    try:
        f.save('data/'+f.filename)
    except Exception as e:
        flash(str(e), 'ERROR')
        return render_template('load.html', action='/load')

    result = Log.load_trades_from(f.filename)

    if result.success:
        flash(f'{f.filename} loaded successfully! There are {result.message} new raw trades',
                'SUCCESS')
    else:
        flash(f'Failed to process {f.filename}. {result.message}', result.severity)   

    return render_template('load.html', action='/load')


@web.route('/raw', methods=['GET', 'POST'])
@login_required
def commit():
    """ Convert a raw trade into a processed trade """
    sortby = request.args.get('sortby')

    if request.method == 'POST':
        result = Log.commit_raw_trade(request.form.get('raw_id'),
                                    request.form.get('port').replace('_',' '))
        flash(result.message, result.severity)

    result=Log.get_raw_trades()

    if not result.success: 
        flash(result.message, result.severity)
        result.message = []
    elif not result.message: flash('There are no raw trades to commit', 'WARNING')
    return render_template('raw_trades.html', trades=_sort(result.message, sortby), ports=[port.name.replace(' ', '_') for port in _ports()])

@web.route('/port/<port>')
@login_required
def port(port):
    """ List the stocks in this port """
    sortby = request.args.get('sortby')

    result = Log.get_stocks(port)
    if not result.success:
        flash(result.message, result.severity)
        result.message = []
    elif not result.message:
        flash("This portfolio contains no stocks. Commit a trade to get started.", "WARNING")
    
    return render_template("stocks.html", port=port, stocks=_sort(result.message, sortby))

@web.route('/port/<port>/<stock>')
@login_required
def stock(port, stock):
    """ List the positions in this stock in this port """
    sortby = request.args.get('sortby')
    what = request.args.get('what')

    open = Log.get_open_positions(port, stock)
    if not open.success: 
        flash(open.message, open.severity)
        open.message=[]
    if not open.message: flash("There are no open positions", "WARNING")
    elif what == 'open': open.message = _sort(open.message, sortby)
    closed = Log.get_closed_positions(port, stock)
    if not closed.success: 
        flash(closed.message, closed.severity)
        closed.message=[]
    elif what == 'closed': closed.message = _sort(closed.message, sortby)
    if not closed.message: flash("There are no closed positions", "WARNING")
    return render_template("stock.html", open=open.message, closed=closed.message, 
                            port=port, stock=stock)

@web.route('/port/<port>/<stock>/open')
@login_required
def open(port, stock):
    """ List the open positions and trades """
    sortby = request.args.get('sortby')
    result = Log.get_open_positions(port=port, stock=stock)
    if not result.success:
        flash(result.message, result.severity)
        result.message = []
    return render_template('open.html', open=_sort(result.message, sortby), port=port, stock=stock)

@web.route('/port/<port>/<stock>/closed')
@login_required
def closed(port, stock):
    """ List closed positions and trades """
    sortby = request.args.get('sortby')
    result = Log.get_closed_positions(port=port, stock=stock)
    if not result.success:
        flash(result.message, result.severity)
        result.message = []
    elif not result.message: flash(f'{stock} has no closed positions', 'WARNING')
    return render_template('closed.html', closed=_sort(result.message, sortby), port=port, stock=stock)

@web.route('/positions/<port>')
@login_required
def positions(port):
    """ List the positions in this port """
    sortby = request.args.get('sortby')
    what = request.args.get('what')

    open = Log.get_open_positions(port, None)
    if not open.success: 
        flash(open.message, open.severity)
        open.message=[]
    if not open.message: flash("There are no open positions", "WARNING")
    elif what == 'open': open.message = _sort(open.message, sortby)
    closed = Log.get_closed_positions(port, None)
    if not closed.success: 
        flash(closed.message, closed.severity)
        closed.message=[]
    elif what == 'closed': closed.message = _sort(closed.message, sortby)
    if not closed.message: flash("There are no closed positions", "WARNING")
    return render_template("positions.html", open=open.message, closed=closed.message, port=port)

@web.route('/open/<port>')
@login_required
def allopen(port):
    """ List the positions in this port """
    sortby = request.args.get('sortby')
    open = Log.get_open_positions(port, None)
    if not open.success: 
        flash(open.message, open.severity)
        open.message=[]
    if not open.message: flash("This portfolio contains no open positions", "WARNING")
    return render_template("all_open.html", open=_sort(open.message, sortby), port=port)

@web.route('/closed/<port>')
@login_required
def allclosed(port):
    """ List the closed positions in this portfolio """
    sortby = request.args.get('sortby')
    closed = Log.get_closed_positions(port, None)
    if not closed.success: 
        flash(closed.message, closed.severity)
        closed.message=[]
    if not closed.message: flash("This portfolio contains no closed positions", "WARNING")
    return render_template("all_closed.html", closed=_sort(closed.message, sortby), port=port)

@web.route('/position/<_id>')
@login_required
def position(_id):
    result = Log.get_trades(_id)
    if not result.success: flash(result.message, result.severity)
    return render_template("trades.html", positions=result.message, position=result.severity)
    
@web.route('/backup')
@login_required
def backup():
    result = Log.backup()
    flash(result.message, result.severity)
    return redirect(request.referrer)

@web.route('/restore')
@login_required
def restore():
    if current_user.is_admin():
        result = Log.restore()
        flash(result.message, result.severity)
    else:    
        flash('This function requires admin priviledges', 'WARNING')
    return redirect(request.referrer)

@web.route('/bulk', methods=['GET', 'POST'])
@login_required
def bulk():
    """ select a file of raw trades to load and auto import """
    if current_user.is_admin():
        if request.method == 'GET': return render_template('load.html', action='/bulk')

        f = request.files['file']
        try:
            f.save('data/'+f.filename)
        except Exception as e:
            flash(str(e), 'ERROR')

        result = Log.bulk(f.filename)
        if not result.success:
            flash(f'Failed to process {f.filename}. {result.message}', result.severity)   

        raw = sorted(result.message, key=lambda x: x['TradeDate'])
        return render_template('bulk.html', raw=raw)
        
    else:    
        flash('This function requires admin priviledges', 'WARNING')
        return redirect(request.referrer)

@web.route('/sharepad', methods=['GET', 'POST'])
@login_required
def sharepad():
    """ Load trades from sharepad instead of IB """
    if request.method == 'GET': 

        return render_template('sharepad.html', ports=[port.name.replace(' ', '_') for port in _ports()])

    if 'port' in request.form.keys(): port = request.form['port'].replace('_', ' ')
    else: port = None

    f = request.files['file']
    try:
        f.save('data/'+f.filename)
    except Exception as e:
        flash(str(e), 'ERROR')
        return render_template('sharepad.html', ports=[port.name.replace(' ', '_') for port in _ports()])

    result = Log.load_sharepad_trades('data/'+f.filename, port)

    if result.success:
        flash(f'{f.filename} loaded successfully!', 'SUCCESS')
    else:
        flash(f'Failed to load {f.filename}. {result.message}', result.severity)

    return render_template('sharepad.html', ports=[port.name.replace(' ', '_') for port in _ports()])

@web.route('/prices')
@login_required
def port_prices():
    return render_template('port_prices.html', ports=_ports())

@web.route('/prices/<port>')
@login_required
def prices(port):
    open = Log.get_open_positions(port, None)
    if not open.success: 
        flash(open.message, open.severity)
        return redirect('/prices')
    if not open.message: flash("This portfolio contains no open positions", "WARNING")

    return render_template('prices.html', prices=Prices.price(open.message))

# private functions

def _ports():
    result = Log.get_ports()
    if not result.success:
        flash(result.message, result.severity)
        result.message = []
    if len(result.message) == 0:
        flash('There are no Portfolios. Create one before proceeding further', 
              'WARNING')
    return result.message

def _sort(items, sortby):
    global reverse 
    reverse = not reverse
    if sortby and items:
        if type(items[0]) == dict: 
            return sorted(items, key=lambda i: i[sortby], reverse=reverse)
        elif 'trade' in vars(items[0]).keys(): return sorted(items, key = lambda i: i.trade[sortby], reverse=reverse)
        return sorted(items, key=operator.attrgetter(sortby), reverse=reverse)
    return items