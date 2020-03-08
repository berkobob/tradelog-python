from flask import flash, render_template
from src.model.mongodb import DB

def process_raw_trades(filename):
    """ load the raw trade file from IB and process each trade """
    trades = []
    try:
        with open(filename) as file:
            headers = file.readline().split(',')
            for row in file:
                # x = DB.add_raw_trade(dict(zip(headers, row.split(','))))
                # print(x)
                trade = dict(zip(headers, row.split(',')))
                trades.append(trade)
    except Exception as e:
        flash(e.strerror, 'ERROR')

    return trades