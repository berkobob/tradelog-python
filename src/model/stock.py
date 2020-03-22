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

        if exists: # Symbol has a position already e.g stock, option etc
            result = exists[0].message.add(trade)
        else: # There are no positions on this symbol yet
            result = Position.new(trade) 
            if result.success: self.open.append(result.message._id)

        if not result.success: return result
        position = result.message

        if not result.success: return result
        position = result.message

        if position.closed:
            self.closed.append(position._id)
            self.open.remove(position._id)
            message = f"this trade was closed for {position.cash} in {position.closed - position.open} days"
        else:   
            if exists: message = f"this trade changed the quatity to {position.quantity}"
            else: message = f"this trade opened the position for {trade.cash}"

        if not exists or position.closed:
            result = self.update({'open': self.open, 'closed': self.closed})
            if not result.success: return result
            
        pre = f"By {trade.bos}ING {trade.quantity} {trade.symbol} "
        return Result(success=True, message=pre+message)

    def get_open_positions(self):
        return [Position.get(id).message for id in self.open]

    def get_closed_positions(self):
        return [Position.get(id).message for id in self.closed]

    def __str__(self):
        return str(vars(self))
