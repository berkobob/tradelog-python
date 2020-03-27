from src.model.model import Model
from src.model.position import Position
from src.common.result import Result
from bson.objectid import ObjectId

class Stock(Model):
    """ An underlying position """
    collection = "stock"

    def __init__(self, trade):
        self.port = trade['port']
        self.stock = trade['stock']
        self.open = trade['open'] 
        self.closed = trade['closed']
        self.proceeds = trade['proceeds']
        self.commission = trade['commission']
        self.cash = trade['cash']
        self._id = trade['_id']

    @classmethod
    def new(cls, trade):
        # create a new stock to add its first trade
        return cls({
            '_id': ObjectId(),
            'port': trade.port, 
            'stock': trade.stock,
            'open': [],
            'closed': [],
            'proceeds': 0.0,
            'commission': 0.0,
            'cash': 0.0,
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
            self.proceeds += position.proceeds
            self.commission += position.commission
            self.cash += position.cash
            severity = "CLOSED"
        else:   
            if exists: severity = "CHANGED"
            else: severity = "OPENED"

        if not exists or position.closed:
            result = self.update(vars(self))
            if not result.success: return result
        
        return Result(success=True, message=position, severity=severity)

    def get_open_positions(self):
        return [Position.get(id).message for id in self.open]

    def get_closed_positions(self):
        return [Position.get(id).message for id in self.closed]

    def get_positions(self):
        positions = self.open + self.closed
        return [Position.get(id).message for id in positions]

    def __str__(self):
        return str(vars(self))
