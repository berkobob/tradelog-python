""" Main tradelog controller """

# Controller rules:
# 1. return  Result class {'success': ?, 'message': ?, 'severity': ?}
# 2. pass db returns back to view to format
# 3. process here

from src.model.portfolio import Portfolio
from src.model.position import Position
from src.model.trade import Trade
from src.common.result import Result
from src.model.raw import Raw

class Log:

    @staticmethod
    def get_port_names() -> Result:
        """ Returns a list of portfolio names """
        result = Portfolio.read({}, many=True)
        if not result.success: return result
        result.message = [port.name for port in result.message]
        return result

    @staticmethod
    def create_portfolio(port: str) -> Result:
        """ createa a new portfolio if the name doesn't already exist """
        return Portfolio.new(port['name'].strip(), port['description'])

    @staticmethod
    def load_trades_from(filename) -> Result:
        """ For each row in the file create a raw trade and return the count """
        count, errors = 0, 0
        try:
            with open(filename) as file:
                headers = file.readline().split(',')
                for row in file:
                    raw = Raw.new(dict(zip(headers, row.split(','))))
                    if raw.success: count += 1
                    else: error += 1
        except Exception as e:
            return Result(success=False, message=str(e), severity='ERROR')
        return Result(success=True, message=(count, errors), severity='SUCCESS')

    @staticmethod
    def get_raw_trades():
        """ Return only raw trades that haven't been committed yet i.e. no port value """
        return Raw.read({'port': None}, many=True)

    @staticmethod
    def commit_raw_trade(_id_str, port):
        """ Commit a raw trade by processing and assigning to a portfolio """

        # If no portfolio selected then return a warning
        if port is None:
            return Result(False, 
                        "No portfolio name selected. Please selecet a portfolio for this trade.",
                        "WARNING")

        # Get the raw trade to be processed by its _id
        result = Raw.get(_id_str)
        if not result.success: return result 
        elif not result.message: 
            return Result(success=False, message=
                        f"The trade with id {_id_str} could not be found in the raw collection",
                        severity='ERROR')
        raw_trade = result.message

        # Get the portfolio to which this trade belongs by the port name
        result = Portfolio.get(port)
        if not result.success: return result
        portfolio = result.message
        if not portfolio: 
            return Result(success=False, message=f"Cannot find portfolio {port} for some reason.", severity="ERROR")

        return portfolio.commit(raw_trade)  # return message here

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

    @staticmethod
    def get_trades(_id):
        result = Position.get(_id)
        if not result.success: return result
        trades = [Trade.get(trade).message for trade in result.message.trades]
        return Result(success=True, message=trades)