from src.model.model import Model
from src.model.position import Position
from src.common.result import Result

class Stock(Model):
    """ An underlying position """
    collection = "stock"

    def __init__(self, trade):
        self.port = trade['port']
        self.stock = trade['stock']
        self.open = trade['open'] 
        self.closed = trade['closed']
        if '_id' in trade.keys(): self._id = trade['_id']

    @classmethod
    def new(cls, trade):
        # create a new stock to add its first trade
        return cls({
            'port': trade.port, 
            'stock': trade.stock,
            'open': [],
            'closed': []
            }).create()

    def add(self, trade):
        """ Add this trade to a new or existing position """
        exists = [Position.get(pos) for pos in self.open 
                    if Position.get(pos).message.symbol == trade.symbol]

        if exists: 
            # result = exists[0] # Symbol has a position already e.g stock, option etc
            result = exists[0].message.add(trade)
        else: 
            result = Position.new(trade) # There are no positions on this symbol yet
            if result.success: self.open.append(result.message._id)

        if not result.success: return result
        position = result.message

        if not result.success: return result
        position = result.message

        if position.closed:
            self.closed.append(position._id)
            self.open.remove(position._id)
            message = f"This trade closed the position for {position.cash}"
        else:   
            if exists: message = f"This trade added to this existing position"
            else: message = f"This trade opened the position"

        if not exists or position.closed:
            result = self.update({'open': self.open, 'closed': self.closed})
            if not result.success: return result
            
        return Result(success=True, message=message)

    def __str__(self):
        return f"{self.stock} in {self.port} has {len(self.open)} open trades and {len(self.closed)} closed trades"
