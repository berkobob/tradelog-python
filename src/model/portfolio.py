from src.model.model import Model
from src.model.trade import Trade
from src.model.stock import Stock
from src.common.result import Result
from bson.objectid import ObjectId

class Portfolio(Model):
    """ A list of stock with share and option positions """
    collection = "portfolios"

    # def __init__(self, port):
    #     self.name = port['name']
    #     self.description = port['description']
    #     self.stocks = port['stocks']
    #     self._id = port['_id']
    #     self.proceeds = port['proceeds']
    #     self.commission = port['commission']
    #     self.cash = port['cash']


    def __init__(self, _id: object, name: str, description: str, stocks: list, proceeds: float,
                commission: float, cash: float):
        self._id = _id
        self.name = name
        self.description = description
        self.stocks = stocks
        self.proceeds = proceeds
        self.commission = commission
        self.cash = cash

    @classmethod
    def new(cls, port, description):
        if port == "":
            return Result(success=False, message="Please provide a portfolio name", severity='WARNING')
        if cls.get(port).success:
            return Result(success=False, message='This portfolio name already exists', 
                        severity='WARNING')
        return cls(**{
            '_id': ObjectId(),
            'name': port,
            'description': description,
            'stocks': [],
            'proceeds': 0.0,
            'commission': 0.0,
            'cash': 0.0
        }).create()

    @classmethod
    def get(cls, port):
        """ Override get method in Model to use port name instead of _id """
        result = cls.read({'name': port})
        if not result.success: return result
        if not result.message: return Result(success=False,
                                             message=f"portfolio {port} not found", 
                                             severity='ERROR')
        return result

    def commit(self, raw):
        """ Get a raw trade, process it into a trade and then add it to this port """
        # Update the raw record with this port name
        result = raw.commit(self.name)
        if not result.success: return result
        
        # Process the raw trade
        result = Trade.new(raw)
        if not result.success: return result
        trade = result.message

        # Add the trade to the stock or create new if first one
        result = Stock.read({'port': self.name, 'stock': trade.stock})
        if not result.success: return result

        if not result.message: # This trade represents a new stock to this port
            result = Stock.new(trade)
            if not result.success: return result
            stock = result.message
            self.stocks.append(stock._id)
            temp = self.update({'stocks': self.stocks})
            if not temp.success: return temp

        result = result.message.add(trade)
        if not result.success: return result
        if result.severity == "CLOSED":
            self.proceeds += result.message.proceeds 
            self.commission += result.message.commission
            self.cash += result.message.cash

        pre = f"By {trade.bos}ING {trade.quantity} {trade.stock} {trade.asset} for {trade.proceeds} this trade was "

        return Result(success=True, message=pre+result.severity)  # return a message about the committed trade

    def get_stocks(self):
        return [Stock.get(id).message for id in self.stocks]

    def get_open_positions(self, stock_name):
        stock = self._get_stock(stock_name)
        return Result(success=True, message=(stock.get_open_positions()))

    def get_closed_positions(self, stock_name):
        stock = self._get_stock(stock_name)
        return Result(success=True, message=(stock.get_closed_positions()))


    # Private functions

    def _get_stock(self, stock):
        search = [Stock.get(id) for id in self.stocks if Stock.get(id).message.stock == stock]
        if search and search[0].success: return search[0].message
        return None

