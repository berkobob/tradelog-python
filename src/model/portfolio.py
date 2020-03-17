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
        if '_id' in port.keys():
            self._id = port['_id']

    def commit(self, raw):
        # Update the raw record with this port name
        raw.port = self.name
        result = raw.update({'port': self.name})
        if not result.success: return result

        # Process the raw trade
        result = Trade.new(raw)
        if not result.success: return result
        trade = result.message

        # Add the trade to the stock or create new if first one
        result = Stock.read({'port': self.name, 'stock': trade.stock})
        if not result.success: return result
        if result.message: 
            stock = result.message[0]
            result = stock.add(trade)
        else: result = Stock.new(trade)
        return result