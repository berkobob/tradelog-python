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
        self.proceeds = port['proceeds']
        self.commission = port['commission']
        self.cash = port['cash']

    @classmethod
    def new(cls, port):
        name = port['name'].strip()
        description = port['description'].strip()
        if name == "": raise AppError('Please provide a portfolio name', 'WARNING')
        if cls.get(name): raise AppError('This portfolio name already exists', 'WARNING')

        return cls({
            '_id': ObjectId(),
            'name': name,
            'description': description,
            'stocks': [],
            'proceeds': 0.0,
            'commission': 0.0,
            'cash': 0.0
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
        if trade.stock in self.stocks: # Yes
            stock = Stock.get(port=self.name, stock=trade.stock)
            assert stock
        else: # This trade represents a new stock to this portfolio
            stock = Stock.new(trade)
            self.stocks.append(stock.stock)
            self.update({'stocks': self.stocks})

        # Process this trade
        position = stock.add(trade)

        if len(position.trades) == 0: msg = 'closed'
        elif len(position.trades) == 1: msg = 'opened'
        else: msg = 'changed'

        print(len(position.trades))

        # If this trade closes the position then update portfolio totals
        if position.closed:
            self.proceeds += position.proceeds 
            self.commission += position.commission
            self.cash += position.cash
            self.update()

        return f"By {trade.bos}ING {abs(trade.quantity)} {trade.stock} {trade.asset} for \
                {trade.proceeds} this position was " + msg
