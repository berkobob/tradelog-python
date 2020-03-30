""" Main tradelog controller """

# Controller rules:
# 1. return  Result class {'success': ?, 'message': ?, 'severity': ?}
# 2. pass db returns back to view to format
# 3. process here

from src.model.portfolio import Portfolio
from src.model.position import Position
from src.model.trade import Trade
from src.common.result import Result
from src.common.exception import AppError
from src.model.raw import Raw

class Log:

    @staticmethod
    def get_port_names() -> Result:
        """ Returns a list of portfolio names """
        try:
            portfolios = Portfolio.read({}, many=True)
        except AppError as e:
            return Result(success=False, message=e.message, severity=e.severity)
        else:
            names = [port.name for port in portfolios]
            return Result(success=True, message=names)

    @staticmethod
    def create_portfolio(port: str) -> Result:
        """ createa a new portfolio if the name doesn't already exist """
        try:
            message = Portfolio.new(port)
        except AppError as e:
            return Result(success=False, message=e.message, severity=e.severity)
        else:
            return Result(success=True, message=message)

    @staticmethod
    def load_trades_from(filename) -> Result:
        """ For each row in the file create a raw trade and return the count """
        count = 0
        try:
            with open(filename) as file:
                headers = file.readline().split(',')
                for row in file:
                    Raw.new(dict(zip(headers, row.split(','))))
                    count += 1
        except Exception as e:
            return Result(success=False, message=str(e), severity='ERROR')
        return Result(success=True, message=count, severity='SUCCESS')

    @staticmethod
    def get_raw_trades():
        """ Return only raw trades that haven't been committed yet i.e. no port value """
        try:
            raw_trades = Raw.read({'port': None}, many=True)
        except AppError as e:
            return Result(success=False, message=e, severity='ERROR')
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
        raw_trade = Raw.get(_id_str)
        assert raw_trade

        # Get the portfolio to which this trade belongs by the port name
        portfolio = Portfolio.get(port)
        assert portfolio

        return Result(success=True, message=portfolio.commit(raw_trade))

    @staticmethod
    def get_stocks(port: str):
        result = Portfolio.get(port)
        if not result.success: return result
        portfolio = result.message
        return Result(True, portfolio.get_stocks())

    @staticmethod
    def get_open_positions(port: str, stock: str):
        result = Portfolio.get(port)
        if not result.success: return result
        return result.message.get_open_positions(stock)

    @staticmethod
    def get_closed_positions(port: str, stock: str):
        result = Portfolio.get(port)
        if not result.success: return result
        return result.message.get_closed_positions(stock)

    # @staticmethod
    # def get_trades(_id):
    #     result = Position.get(_id)
    #     if not result.success: return result
    #     trades = [Trade.get(trade).message for trade in result.message.trades]
    #     return Result(success=True, message=trades)