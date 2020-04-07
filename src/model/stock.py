from src.model.model import Model
from src.model.position import Position
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
        self.risk = trade['risk']

    @classmethod
    def new(cls, port, stock):
        # create a new stock to add its first trade
        return cls({
            '_id': ObjectId(),
            'port': port, 
            'stock': stock,
            'open': 0,
            'closed': 0,
            'proceeds': 0.0,
            'commission': 0.0,
            'cash': 0.0,
            'risk': 0.0
            }).create()

    @classmethod
    def get(cls, port, stock):
        """ Override model's get to use the stock name instead of _id """
        return cls.read({'port': port, 'stock': stock})

    def add(self, trade):
        """ Add this trade to a new or existing position and return the position """
        position = Position.find(trade.port, trade.symbol) # Does position already exist
        if position: position.add(trade)
        else: 
            position = Position.new(trade)
            self.open += 1

        self.risk = position.risk

        if position.closed:
            self.closed += 1
            self.open -= 1
            self.proceeds += position.proceeds
            self.commission += position.commission
            self.cash += position.cash

        print(self.update())
        return position
