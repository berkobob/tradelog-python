from src.model.model import Model
from src.common.result import Result

class Position(Model):
    """
    Represents a series of trades until flat
    """
    collection = "position"

    def __init__(self, pos):
        if '_id' in pos.keys(): self._id = pos['_id']
        self.port = pos['port']
        self.symbol = pos['symbol']
        self.open = pos['open']
        self.closed = False
        self.stock = pos['stock']
        self.trades = pos['trades']
        self.quantity = pos['quantity']
        self.commission = pos['commission']
        self.cash = pos['cash']

    @classmethod
    def new(cls, trade):
        position = cls({
            'port': trade.port,
            'symbol': trade.symbol,
            'open': trade.date,
            'stock': trade.stock,
            'trades': [trade._id],
            'quantity': trade.quantity,
            'commission': trade.commission,
            'cash': trade.cash
        })
        return position.create()

    def add(self, trade):
        self.trades.append(trade._id)
        self.quantity += trade.quantity
        self.commission += trade.commission
        self.cash += trade.cash
        if self.quantity == 0: self.closed = trade.date
        return self.update(vars(self))
