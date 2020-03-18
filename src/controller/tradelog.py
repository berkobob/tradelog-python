""" Main tradelog controller """

# Controller rules:
# 1. return  Result class {'success': ?, 'message': ?, 'severity': ?}
# 2. pass db returns back to view to format
# 3. process here

from src.model.portfolio import Portfolio
from src.common.result import Result
from src.model.raw import Raw

class Log:

    @staticmethod
    def get_port_names() -> Result:
        """ Returns a list of portfolio names """
        result = Portfolio.read({}, many=True)
        if not result.success: return result
        ports = result.message
        # As Log doesn't keep a list of ports we read the db
        result.message = [port.name for port in ports]
        return result

    @staticmethod
    def create_portfolio(port) -> Result:
        """ createa a new portfolio if the name doesn't already exist """
        port['name'] = port['name'].strip()
        if port['name'] == "":
            return Result(success=False, message="Portfolio name cannot be blank", severity='WARNING')
        if port['name'] in Log.get_port_names().message:
            return Result(success=False, message='This portfolio name already exists', 
                        severity='WARNING')
        return Portfolio(port).create()

    @staticmethod
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
        result = Portfolio.read({'name': port})
        if not result.success: return result
        portfolio = result.message
        if not portfolio: 
            return Result(success=False, message=f"Cannot find portfolio {port} for some reason.", severity="ERROR")

        return portfolio.commit(raw_trade)

    @staticmethod
    def get_stocks(port: str):
        result = Portfolio.read({'name': port})
        if not result.success: return result
        portfolio = result.message

        return Result(True, portfolio.get_stocks())