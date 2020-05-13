from src.model.model import Model
from src.model.position import Position
from bson.objectid import ObjectId

class Stock(Model):
    """ An underlying position """
    collection = "stocks"

    def __init__(self, trade):
        self._id = trade['_id']
        self.port = trade['port']
        self.stock = trade['stock']
        self.open = trade['open'] 
        self.closed = trade['closed']
        self.proceeds = trade['proceeds']
        self.commission = trade['commission']
        self.cash = trade['cash']
        self.risk = trade['risk']


    @classmethod
    def get(cls, port, stock):
        """ Override model's get to use the stock name instead of _id """
        return cls.read({'port': port, 'stock': stock})

    @classmethod
    def commit(cls, raw):
        raw.stock = cls._parse(raw.trade['Symbol']) # Add stock name to raw trade
        result = Position.commit(raw)
        stock = cls.get(raw.port, raw.stock) # Does this stock exist for this portfolio
        if stock: # This trade represents a new stock for this port
            return stock.add(result)
        result['port'] = raw.port
        result['stock'] = raw.stock
        return cls.new(result)

    @classmethod
    def new(cls, result):
        # create a new stock to add its first trade
        result['_id'] = ObjectId()
        cls(result).create()
        result['stocks'] = 1
        return result

    def add(self, result):
        """ Add this trade to a new or existing position and return the position """
        self.open += result['open'] 
        self.closed += result['closed']
        self.proceeds += result['proceeds']
        self.commission += result['commission']
        self.cash += result['cash']
        self.risk += result['risk']
        self.update()
        return result

    def to_json(self):
        json = vars(self)
        json['_id'] = str(self._id)
        return json


    # Private functions
    @staticmethod
    def _parse(symbol: str) -> str:
        stock = symbol.split(' ')[0]
        if stock[-1].isalpha(): return stock
        return stock[0:-1]
