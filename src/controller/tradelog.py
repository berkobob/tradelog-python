""" Main tradelog controller """

# Controller rules:
# 1. return  Result class {'success': ?, 'message': ?, 'severity': ?}
# 2. pass db returns back to view to format
# 3. process here

from src.model.portfolio import Portfolio
from src.common.result import Result
from src.model.raw import Raw
from bson.objectid import ObjectId

def get_port_names() -> Result:
    """ Returns a list of portfolio names """
    result = Portfolio.read({})
    if not result.success: return result
    result.message = [port.name for port in Portfolio.read({}).message]
    return result

def create_portfolio(port) -> Result:
    """ createa a new portfolio if the name doesn't already exist """
    port['name'] = port['name'].strip()
    if port['name'] == "":
        return Result(success=False, message="Portfolio name cannot be blank", severity='WARNING')
    if port['name'] in get_port_names().message:
        return Result(success=False, message='This portfolio name already exists', 
                      severity='WARNING')
    return Portfolio(port).create()

def load_trades_from(filename) -> Result:
    """ Read trades from a CSV file. Store the raw data and pass back with
        a UUID to ID trade and store as a trade"""
    count = 0
    try:
        with open(filename) as file:
            headers = file.readline().split(',')
            for row in file:
                raw = Raw(dict(zip(headers, row.split(','))))
                raw.create()
                count += 1
    except Exception as e:
        return Result(success=False, message=str(e), severity='ERROR')

    return Result(success=True, message=count)

def get_raw_trades():
    return Raw.read({})

def commit_raw_trade(_id_str, port):
    if port is None:
        return Result(False, "No portfolio name selected. Please selecet a portfolio for this trade.",
        "WARNING")

    _id = ObjectId(_id_str)
    result = Raw.read({'_id': _id})
    if not result.success: return result

    portfolio = Portfolio.read({'name': port})
    # Assume, as searching by _id, that only one record found
    if len(portfolio.message) < 1: 
        return Result(success=False, message=f"Cannot find portfolio {port} for some reason.", severity="ERROR")
    if len(portfolio.message) > 1:
        return Result(success=False, message=f"Found multiple portfolios called {port} for some reason.", severity="ERROR")
    return portfolio.message[0].commit(result.message[0])