from flask import Blueprint, render_template, request, flash, redirect
from src.controller.load import process_raw_trades

web = Blueprint('web', __name__)

@web.route('/')
def index():
    return render_template('home.html')

@web.route('/load', methods=['GET', 'POST'])
def load():
    if request.method == 'POST':
        f = request.files['file']
        try:
            f.save(f.filename)
        except Exception as e:
            flash(e.strerror, 'ERROR')
            return render_template('load.html')

        flash(f'{f.filename} loaded successfully!', 'SUCCESS')
        return render_template('rawtrades.html', trades=process_raw_trades(f.filename))

    return render_template('load.html')