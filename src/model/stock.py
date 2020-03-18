from src.model.model import Model
from src.model.position import Position
from src.common.result import Result

class Stock(Model):
    """ An underlying position """
    collection = "stock"

    def __init__(self, trade):
        self.port = trade['port']
        self.stock = trade['stock']
        self.trades = trade['trades']
        self.open = trade['open'] if 'open' in trade.keys() else []
        self.closed = trade['closed'] if 'closed' in trade.keys() else []
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
        result = stock.add(trade)
        if not result.success: return result
        return Result(success=True, message={'stock': stock.stock, '_id': stock._id})

    def add(self, trade):
        self.trades.append(trade._id)
        self._process(trade)
        result = self.update({'trades': self.trades})
        return result

    def __str__(self):
        return f"{self.stock} in {self.port} has {len(self.open)} open trades and {len(self.closed)} closed trades"

    def _process(self, trade):
        """ 
        Open a new position
        Add to a position
        Close a position
        """
        result = [Position.get(pos) for pos in self.open 
                    if Position.get(pos).message.symbol == trade.symbol]

        if result:
            result = result[0]
            if not result.success: return result
            position = result.message
            result = position.add(trade)
            if not result.success: return result
            position = result.message
            if position.closed:
                self.closed.append(position._id)
                self.open.remove(position._id)
                result = self.update({'open': self.open, 'closed': self.closed})
        else:   
            result = Position.new(trade)
            if not result.success: return result
            position = result.message
            self.open.append(position._id)
            result = self.update({'open': self.open})
            
        return result