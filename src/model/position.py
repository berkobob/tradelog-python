from src.model.model import Model
from src.common.result import Result
from bson.objectid import ObjectId

class Position(Model):
    """
    Represents a series of trades until flat
    """
    collection = "position"

    def __init__(self, position):
        self._id = position['_id']
        self.port = position['port']
        self.symbol = position['symbol']
        self.stock = position['stock']
        self.open = position['open']
        self.closed = position['closed'] 
        self.trades = position['trades']
        self.quantity = position['quantity']
        self.commission = position['commission']
        self.proceeds = position['proceeds']
        self.cash = position['cash']
        self.days = position['days']
        self.rate = position['rate']

    @classmethod
    def new(cls, trade):
        return cls({
            '_id': ObjectId(),
            'port': trade.port,
            'symbol': trade.symbol,
            'open': trade.date,
            'closed': False,
            'stock': trade.stock,
            'trades': [trade._id],
            'quantity': trade.quantity,
            'commission': trade.commission,
            'proceeds': trade.proceeds,
            'cash': trade.cash,
            'days': 0,
            'rate': 0.0
        }).create()

    @classmethod
    def get(cls, port, symbol):
        """ Override model's get to use the stock name instead of _id """
        return cls.read({'port': port, 'symbol': symbol})

    def add(self, trade):
        self.trades.append(trade._id)
        self.quantity += trade.quantity
        self.commission += trade.commission
        self.proceeds += trade.proceeds
        self.cash += trade.cash
        if self.quantity == 0: # Then the position is closed
            self.closed = trade.date
            self.days = (self.closed - self.open).days
            self.rate = self.proceeds / self.days
        return self.update()
