from src.model.model import Model
from src.common.result import Result
from bson.objectid import ObjectId

class Stock(Model):
    """ An underlying position """
    collection = "stock"

    def __init__(self, trade):
        self.port = trade['port']
        self.stock = trade['stock']
        self.trades = trade['trades']
        if '_id' in trade.keys(): self._id = trade['_id']

    @classmethod
    def new(cls, trade):
        # create a new stock to add its first trade
        stock = cls({
            'port': trade.port, 
            'stock': trade.stock,
            'trades': []
            })
        result = stock.create()
        if not result.success: return result

        # set _id and add first trade
        stock._id = ObjectId(result.message)
        return stock.add(trade)

    def add(self, trade):
        self.trades.append(trade._id)
        result = self.update({'trades': self.trades})
        return result

    def __str__(self):
        return f"{self.stock} in {self.port} has {len(self.trades)} trades"