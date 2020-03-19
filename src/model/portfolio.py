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

        if not result.message: # This trade represents a new stock to this port
            result = Stock.new(trade)
            if not result.success: return result
            stock = result.message
            self.stocks.append(stock._id)
            temp = self.update({'stocks': self.stocks})
            if not temp.success: return temp

        stock = result.message
        print('By now we should have a stock new or used\n', stock)
        return stock.add(trade)  # return a message about the committed trade

    def get_stocks(self):
        return [str(x) for x in[Stock.get(x).message for x in [stock['_id'] for stock in self.stocks]]]