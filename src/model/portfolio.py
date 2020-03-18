from src.model.model import Model
from src.model.trade import Trade
from src.model.stock import Stock
from src.common.result import Result

class Portfolio(Model):
    """ A list of stock with share and option positions """
    collection = "portfolios"

    def __init__(self, port):
        self.name = port['name']
        self.description = port['description']
        self.stocks = port['stocks'] if 'stocks' in port.keys() else []
        if '_id' in port.keys():
            self._id = port['_id']

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
        if result.message: # already exists
            result = result.message.add(trade)
        else: # a new stock for this port
            result = Stock.new(trade)
            if not result.success: return result
            self.stocks.append(result.message)
            result = self.update({'stocks': self.stocks})
        return result

    def get_stocks(self):
        return [str(x) for x in[Stock.get(x).message for x in [stock['_id'] for stock in self.stocks]]]