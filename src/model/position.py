from src.model.model import Model
from src.model.trade import Trade
from bson.objectid import ObjectId

class Position(Model):
    """
    Represents a series of trades until flat
    There can be only one position in a stock's open list with a specific symbol
    """
    collection = "positions"

    def __init__(self, position):
        self._id = position['_id']
        self.position = position['position']
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
        self.risk_per = position['risk_per']
        self.risk = position['risk']

    @classmethod
    def find(cls, port, symbol, open=False):
        """ Find a position on this symbol for this port """
        if open: return cls.read({'port': port, 'symbol': symbol, 'closed': False})
        return cls.read({'port': port, 'symbol': symbol})

    @classmethod
    def commit(cls, raw):
        trade = Trade.new(raw) # Create a trade from the raw trade
        position = Position.find(raw.port, raw.trade['Symbol'], True)
        if position: return position.add(trade)
        else: return cls.new(trade)

    @classmethod
    def new(cls, trade):
        risk_per = trade.risk()
        position = cls({
            '_id': ObjectId(),
            'position': cls._position(trade),
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
            'risk': risk_per * trade.quantity,
            'risk_per': risk_per,
        })
        position.create()
        return trade.build_result(pos=position.position, risk_per=risk_per, open=1)

    def add(self, trade):
        self.trades.append(trade._id)
        self.quantity += trade.quantity
        self.commission += trade.commission
        self.proceeds += trade.proceeds
        self.cash += trade.cash

        if self.quantity == 0: self._close_position(trade)
        self.risk += trade.risk() * trade.quantity
        self.update()

        if self.closed:
            result = trade.build_result(pos=self.position, risk_per=self.risk_per, open=-1, closed=1)
            result['proceeds'] = self.proceeds
            result['commission'] = self.commission
            result['cash'] = self.cash
            return result
        
        return trade.build_result(pos=self.position, risk_per=self.risk_per)

    def to_json(self):
        json = vars(self)
        json['_id'] = str(self._id)
        json['trades'] = [str(id) for id in self.trades]
        return json

    # Private functions

    def _close_position(self, trade):
        self.closed = trade.date
        self.days = abs((self.closed - self.open).days)
        if self.days == 0: self.days = 1
        self.rate = self.proceeds / self.days
        if self.risk > 0: self.risk = self.proceeds / self.risk

    @staticmethod
    def _position(trade):
        los = "Long" if trade.quantity > 0 else "Short"
        if trade.asset == 'STK': name = f'{los} {trade.symbol} shares'
        else:
            expiry = trade.expiry.strftime("%b %y")
            strike = "${:,.2f}".format(trade.strike)
            name = f"{los} {expiry}, {strike} {trade.poc}"
        return name

