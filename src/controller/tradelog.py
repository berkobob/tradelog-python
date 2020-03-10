""" Main tradelog controller """

# Controller rules:
# 1. return {'success': ?, 'message': ?, 'severity': ?}
# 2. pass db returns back to view to format
# 3. process here

from src.model.mongodb import DB

portfolios = []

def init(db_url, db):
    global portfolios
    DB.connect(db_url, db)
    portfolios = DB.get_portfolios()
    print(portfolios)
    return {'success': True}

def new_portfolio(port):
    if port['name'] in get_portfolio_names():
        msg = f'{port["name"]} already exists. Portfolio not created'
        return {'success': False, 'message': msg, 'severity': 'WARNING'}
    else:
        portfolios.append(port)
        return DB.new_port(port)

def get_portfolio_names():
    global portfolios
    return [port['name'] for port in portfolios if 'name' in port]