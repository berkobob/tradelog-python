""" Main tradelog controller """

# Controller rules:
# 1. return  Result class {'success': ?, 'message': ?, 'severity': ?}
# 2. pass db returns back to view to format
# 3. process here

from src.model.portfolio import Portfolio
from src.model.stock import Stock
from src.model.position import Position
from src.model.trade import Trade
from src.model.raw import Raw
from src.model.price import Price
from src.common.result import Result
from src.common.exception import AppError
from src.common.database import DB
from datetime import datetime
import json

class TradeLog:

    @staticmethod
    def get_ports() -> Result:
        """ Returns a list of portfolio names """
        try:
            portfolios = Portfolio.read({}, many=True)
        except AppError as e:
            return Result(success=False, message="log.get_port_names: "+e.message, severity=e.severity)
        else:
            for portfolio in portfolios:
                portfolio.positions = portfolio.open + portfolio.closed
            return Result(success=True, message=portfolios)

    @staticmethod
    def create_portfolio(port: Portfolio) -> Result:
        """ createa a new portfolio if the name doesn't already exist """
        try:
            message = Portfolio.new(port)
        except AppError as e:
            return Result(success=False, message="create_portfolio: "+str(e), severity=e.severity)
        else:
            return Result(success=True, message=message)

    @staticmethod
    def load_trades_from(filename: str) -> Result:
        """ For each row in the file create a raw trade and return the count """
        count = 0
        try:
            with open('data/'+filename) as file:
                headers = file.readline().rstrip('\n').replace('"', '').split(',')
                for row in file: # Assuming all .csv data is valid
                    Raw.new(dict(zip(headers, row.rstrip('\n').replace('"', '').split(','))))
                    count += 1
        except Exception as e:
            return Result(success=False, message="log.load_trades_from: "+str(e), severity='ERROR')
        return Result(success=True, message=count, severity='SUCCESS')

    @staticmethod
    def get_raw_trades():
        """ Return only raw trades that haven't been committed yet i.e. no port value """
        try:
            raw_trades = Raw.read({'port': None}, many=True)
        except AppError as e:
            return Result(success=False, message="log.get_raw_trades: "+e, severity='ERROR')
        else:
            return Result(success=True, message=raw_trades)

    @staticmethod
    def commit_raw_trade(_id_str, port):
        """ Commit a raw trade by processing and assigning to a portfolio """

        # If no portfolio selected then return a warning
        if port is None:
            return Result(False, 
                        "No portfolio name selected. Please selecet a portfolio for this trade.",
                        "WARNING")

        # Get the raw trade to be processed by its _id
        try:
            raw_trade = Raw.get(_id_str)
            assert raw_trade
        except AppError as e:
            return Result(success=False, message="log.commit_raw_trade: "+str(e), severity="ERROR")
        except AssertionError:
            return Result(success=False, 
                          message=f"log.commit_raw_trade: Raw trade with id {_id_str} not found",
                          severity='ERROR')

        # Get the portfolio to which this trade belongs by the port name
        try: 
            portfolio = Portfolio.get(port)
            assert portfolio
        except AppError as e:
            return Result(success=False, message="log.commit_raw_trade: "+str(e), severity='ERROR')
        except AssertionError:
            return Result(success=False, 
                          message=f"log.commit_raw_trade: Portfolio {port} not found",
                          severity='ERROR')

        if 'currency' not in raw_trade.trade.keys():
            raw_trade.trade['currency'] = '$'

        try:
            # Actually commit the trade
            result = portfolio.commit(raw_trade)
            # If it's a new stock add it to the prices table
            if result['stocks']: Price.new(raw_trade)
            message = TradeLog._parse_msg(result, raw_trade.trade['Quantity'])
        except AppError as e:
            return Result(success=False, message="log.commit_raw_trade: "+str(e), severity='ERROR')

        return Result(success=True, message=message, severity='SUCCESS')

    @staticmethod
    def get_stocks(port: str):
        """ Return a list of stock traded in this portfolio """
        try:
            stocks = Stock.read({'port': port}, many=True)
        except AppError as e:
            result = Result(success=False, message=e, severity='WARNING')
        else:
            result = Result(success=True, message = stocks)
        return result

    @staticmethod
    def get_open_positions(port, stock=None):
        try:
            if stock: positions = Position.read({'port': port, 'stock': stock, 'closed': False}, many=True)
            else: positions = Position.read({'port': port, 'closed': False}, many=True)
        except AppError as e:
            return Result(success=False, message=e)
        else:
            for position in positions:
                position.trades = len(position.trades)
                position.days = (datetime.now()-position.open).days
            return Result(success=True, message=positions)

    @staticmethod
    def get_closed_positions(port: str, stock: str):
        try:
            if stock: positions = Position.read({'port': port, 'stock': stock, 'closed': {'$ne': False}}, many=True)
            else: positions = Position.read({'port': port, 'closed': {'$ne': False}}, many=True)
        except AppError as e:
            return Result(success=False, message=e)
        else:
            for position in positions:
                position.trades = len(position.trades)
            return Result(success=True, message=positions)

    @staticmethod
    def get_positions(port:str, stock:str):
        try:
            positions = Position.read({'port': port, 'stock': stock}, many=True)
        except AppError as e:
            return Result(success=False, message=e)
        else:
            return Result(success=True, message=positions)

    @staticmethod
    def get_trades(pos_id: str):
        try:
            position = Position.get(pos_id)
            trades = [Trade.get(trade) for trade in position.trades]
        except AppError as e:
            return Result(success=False, message=e)
        else:
            return Result(success=True, message=trades, severity=position.position)

    @staticmethod
    def backup():
        ports = [{'name': port.name, 'description': port.description} \
                for port in Portfolio.read({}, many=True)]
        with open('data/portfolios.json', 'w') as f:
            json.dump([{'name': port['name'], 'description': port['description']} \
                        for port in ports], f)

        trades = [{'trade': raw.trade, 'port': raw.port} for raw in Trade.read({'port': {'$ne': None}}, many=True)]
        with open('data/trades.json', 'w') as f:
            json.dump(trades, f)

        raw = [{'trade': raw.trade} for raw in Raw.read({'port': None}, many=True)]
        with open('data/raw.json', 'w') as f:
            json.dump(raw, f)

        return Result(success=True, 
            message=f'Successfully backed up {len(ports)} portfolios, {len(trades)} trades and {len(raw)} raw trades',
            severity='SUCCESS')

    @staticmethod
    def restore():
        DB.drop()
        with open('data/portfolios.json', 'r') as f:
            portfolios = json.load(f)

        for portfolio in portfolios:
            try:
                Portfolio.new(portfolio)
            except Exception as e:
                return Result(success=False, message=str(e), severity='ERROR')

        with open('data/trades.json', 'r') as f:
            trades = json.load(f)
            trades.sort(key=lambda i: (i['port'], i['trade']['TradeDate']))

        [TradeLog.commit_raw_trade(Raw.new(trade['trade']._id), trade['port']) for trade in trades]

        with open('data/raw.json', 'r') as f:
            raw = json.load(f)

        [Raw.new(r) for r in raw]

        return Result(success=True, 
            message=f'Successfully restored {len(portfolios)} portfolios, {len(trades)} trades and \
                    {len(raw)} raw trades', severity='SUCCESS')

    @staticmethod
    def bulk(filename: str) -> Result:
        try:
            with open('data/'+filename) as file:
                headers = file.readline().rstrip('\n').split(',')
                raw = [dict(zip(headers, row.rstrip('\n').split(','))) for row in file]
        except Exception as e:
            return Result(success=False, message="log.load_trades_from: "+str(e), severity='ERROR')

        raw.sort(key = lambda x: x['TradeDate'])

        ports = [port.name for port in TradeLog.get_ports().message]
        for r in raw:
            if not r['Portfolio'] in ports: TradeLog.create_portfolio({'name': r['Portfolio'], 'description': 'Created by bulk upload'})
            r['msg'] = TradeLog.commit_raw_trade(Raw.new(r)._id, r['Portfolio']).message

        return Result(success=True, message=raw, severity='SUCCESS')

    @staticmethod
    def load_sharepad_trades(filename, port):
        try:
            with open(filename) as file:
                headers = file.readline().replace('\ufeff','').split(',')
                for row in file:
                    trade = dict(zip(headers, row.split(',')))
                    if trade['Name'] == 'Buy' or trade['Name'] == 'Sell':
                        trade['Buy/Sell'] = trade['Name']
                        trade['Quantity'] = trade['Shares'] if trade['Name'] == 'Buy' else '-'+trade['Shares']
                        trade['Symbol'] = trade['TIDM']
                        trade['Strike'] = False
                        trade['Put/Call'] = False
                        trade['TradePrice'] = trade['Price']
                        trade['Proceeds'] = trade['Cost']
                        trade['IBCommission'] = "0.0"
                        trade['NetCash'] = trade['Cost']
                        trade['AssetClass'] = 'STK'
                        if trade['Name'] == 'Buy': trade['Open/CloseIndicator'] = 'O'
                        if trade['Name'] == 'Sell': trade['Open/CloseIndicator'] = 'C'
                        trade['Multiplier'] = '1'
                        trade['Notes/Codes'] = trade['Name']
                        trade['currency'] = '£'
                        raw = Raw.new(trade)._id
                        if port: TradeLog.commit_raw_trade(raw, port)
        except Exception as e:
            return Result(False, 'log.load_sharepad_trades: '+str(e), 'ERROR')

        return Result(True, message='Phew')

    @staticmethod
    def price():
        message = []
        try:
            for port in TradeLog.get_ports().message:
                positions = [position for position in TradeLog.get_open_positions(port.name).message]
                message.append({
                    'port': port.name,
                    'value': sum(price['value'] for price in Price.get_price(positions))
                })
        except Exception as e:
            return Result(False, message=str(e), severity='ERROR')
        return Result(True, message)

    @staticmethod
    def prices():
        return Price.read({}, True)

    @staticmethod
    def update():
        Price.update_prices()

    @staticmethod
    def delete_price(stock):
        try:
            Price.get(stock).delete()
        except Exception as e:
            return Result(success=False, message=f"Failed to delete {stock}: {str(e)}", severity='WARNING')
        return Result(success=True, message=f"Successfully delete {stock}")

    # Private function

    @staticmethod
    def _parse_msg(result, qty):
        proceeds = '${:,.2f}'.format(float(result['proceeds']))
        risk = '${:,.2f}'.format(float(result['risk']))
        msg = ""
        if result['stocks']: msg = " on a new stock"
        if result['closed']: return f"CLOSE {result['pos']} on {result['stock']} for {proceeds}"
        if result['open']: return f"OPEN {abs(int(qty))} {result['pos']} on {result['stock']} risking {risk}{msg}"
        return f"CHANGE qty of {result['pos']} on {result['stock']} by {qty}. Risk change: {risk}"
        