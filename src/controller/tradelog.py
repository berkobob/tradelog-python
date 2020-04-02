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
from src.common.result import Result
from src.common.exception import AppError
from datetime import datetime

class Log:

    @staticmethod
    def get_port_names() -> Result:
        """ Returns a list of portfolio names """
        try:
            portfolios = Portfolio.read({}, many=True)
        except AppError as e:
            return Result(success=False, message="log.get_port_names: "+e.message, severity=e.severity)
        else:
            names = [portfolio.name for portfolio in portfolios]
            return Result(success=True, message=names)

    @staticmethod
    def create_portfolio(port: str) -> Result:
        """ createa a new portfolio if the name doesn't already exist """
        try:
            message = Portfolio.new(port)
        except AppError as e:
            return Result(success=False, message="create_portfolio: "+e.message, severity=e.severity)
        else:
            return Result(success=True, message=message)

    @staticmethod
    def load_trades_from(filename: str) -> Result:
        """ For each row in the file create a raw trade and return the count """
        count = 0
        try:
            with open(filename) as file:
                headers = file.readline().split(',')
                for row in file: # Assuming all .csv data is valid
                    Raw.new(dict(zip(headers, row.split(','))))
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

        try:
            message = portfolio.commit(raw_trade)
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
            result = Result(success=True,
                            message = [{'stock': stock.stock, 
                        'positions': len(stock.open)+len(stock.closed), 
                        'open': len(stock.open), 
                        'closed': len(stock.closed),
                        'proceeds': stock.proceeds,
                        'commission': stock.commission,
                        'cash': stock.cash
                        } for stock in stocks])
        return result

    @staticmethod
    def get_open_positions(port: str, stock: str):
        try:
            positions = Position.read({'port': port, 'stock': stock, 'closed': False}, many=True)
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
            positions = Position.read({'port': port, 'stock': stock, 'closed': {'$ne': False}}, many=True)
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
            return Result(success=True, message=trades, severity=position.asset)