from src.model.model import Model
from bson.objectid import ObjectId

class Position(Model):
    """
    Represents a series of trades until flat
    There can be only one position in a stock's open list with a specific symbol
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
        self.position = position['position'] or "Wow"
        self.risk = position['risk']

    @classmethod
    def new(cls, trade):
        return cls({
            '_id': ObjectId(),
            'port': trade.port,
            'symbol': trade.symbol,
            'open': trade.date,
            'closed': False,
            'stock': trade.stock,
            'trades': [trade._id], # Only way to find a trade
            'quantity': trade.quantity,
            'commission': trade.commission,
            'proceeds': trade.proceeds,
            'cash': trade.cash,
            'days': 0,
            'rate': 0.0,
            'position': cls._position(trade),
            'risk': cls._risk(trade)
        }).create()

    @classmethod
    def find(cls, port, symbol):
        """ Find a position on this symbol for this port """
        return cls.read({'port': port, 'symbol': symbol})

    def add(self, trade):
        self.trades.append(trade._id)
        self.quantity += trade.quantity
        self.commission += trade.commission
        self.proceeds += trade.proceeds
        self.cash += trade.cash
        if self.quantity == 0: # Then the position is closed
            if self.risk == 0: self.risk = self._risk(trade) # closing trade committed first
            self.closed = trade.date
            self.days = (self.closed - self.open).days
            if self.days == 0: self.days = 1
            self.rate = self.proceeds / self.days
            if self.risk != 0: self.risk = self.proceeds / self.risk
            if self.closed < self.open: self.position = self._position(trade)
        else:
            self.risk = self._risk(trade)
        print(self.update())
        return self

    @staticmethod
    def _position(trade):
        los = "Long" if trade.quantity > 0 else "Short"
        if trade.asset == 'STK': name = f'{los} {trade.symbol} shares'
        else:
            expiry = trade.expiry.strftime("%b %y")
            strike = "${:,.2f}".format(trade.strike)
            name = f"{los} {expiry}, {strike} {trade.poc}"
        return name

    @staticmethod
    def _risk(trade):
        if trade.ooc == 'O':
            if trade.asset == 'STK' and trade.quantity > 0: 
                return trade.quantity * trade.price * trade.multiplier
            if trade.asset == 'OPT':
                return trade.strike * trade.multiplier - trade.proceeds
        return 0