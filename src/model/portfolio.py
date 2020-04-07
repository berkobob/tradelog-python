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
        # Update the raw record with this port name & create a trade
        raw.commit(self.name)
        trade = Trade.new(raw)

        # Does the stock exist in this portfolio
        stock = Stock.get(self.name, trade.stock)
        if not stock: # This trade represents a new stock to this portfolio
            stock = Stock.new(self.name, trade.stock)
            self.stocks += 1
            self.update({'stocks': self.stocks})

        # Process this trade
        risk = stock.risk
        position = stock.add(trade)
        risk = stock.risk - risk
        print('Change in risk is ', risk)

        # Assume no change at port level unless...
        msg = 'changed'

        # Only having one trade means it much be a new position
        if len(position.trades) == 1: 
            msg = 'opened'
            self.open += 1
            self.risk += position.risk

        # If this trade closes the position then update portfolio totals
        if position.closed:
            self.proceeds += position.proceeds 
            self.commission += position.commission
            self.cash += position.cash
            msg = 'closed'
            self.closed += 1
            self.open -= 1
            self.risk -= risk

        self.update()

        x = f"By {trade.bos}ING {abs(trade.quantity)} {trade.stock} {trade.asset} for \
                {trade.proceeds} this position was " + msg
        if msg == "closed": return x
        return msg + ". The position has a risk of " + str(position.risk)