from src.model.model import Model
from src.model.trade import Trade
from src.model.stock import Stock
from bson.objectid import ObjectId
from src.common.exception import AppError

class Portfolio(Model):
    """ A list of stock with share and option positions """
    collection = "portfolios"

    def __init__(self, port):
        self._id = port['_id']
        self.name = port['name']
        self.description = port['description']
        self.stocks = port['stocks']
        self.open = port['open'] # positions?
        self.closed = port['closed'] # positions?
        self.proceeds = port['proceeds'] # closed positions
        self.commission = port['commission'] # closed positions
        self.cash = port['cash'] # closed positions
        self.risk = port['risk'] # open positions

    @classmethod
    def new(cls, port):
        """ Create a portfolio name and description. Only class that doesn't need a trade to be created """
        name = port['name'].strip()
        description = port['description'].strip()
        if name == "": raise AppError('Please provide a portfolio name', 'WARNING')
        if cls.get(name): raise AppError('This portfolio name already exists', 'WARNING')

        return cls({
            '_id': ObjectId(),
            'name': name,
            'description': description,
            'stocks': 0,
            'open': 0,
            'closed': 0,
            'proceeds': 0.0,
            'commission': 0.0,
            'cash': 0.0,
            'risk': 0.0
        }).create()

    @classmethod
    def get(cls, port):
        """ Override get method in Model to use port name instead of _id """
        return cls.read({'name': port})

    def commit(self, raw):
        """ Get a raw trade, process it into a trade and then add it to this port """

        raw.port = self.name # Add port name to raw trade
        result = Stock.commit(raw) # Send the raw trade to the stock class

        self.stocks += result['stocks']
        self.open += result['open'] # positions?
        self.closed += result['closed'] # positions?
        self.proceeds += result['proceeds'] # closed positions
        self.commission += result['commission'] # closed positions
        self.cash += result['cash'] # closed positions
        self.risk += result['risk'] # open positions
        self.update()

        return result

    def to_json(self):
        json = vars(self)
        json['_id'] = str(self._id)
        return json