from src.model.model import Model
from src.common.result import Result
from datetime import datetime

class Trade(Model):
    """ buying or selling a stock or option """
    collection = "trade"

    def __init__(self, trade):
        self.date = datetime.strptime(trade['TradeDate'], "%Y%m%d")
        self.bos = trade['Buy/Sell']
        self.quantity = int(trade['Quantity'])
        self.symbol = trade['Symbol']
        self.stock = _parse(trade['Symbol'])
        self.expiry = datetime.strptime(trade['Expiry'], "%d/%m/%Y") if trade['Expiry'] else None
        self.strike = float(trade['Strike']) if trade['Strike'] else None
        self.poc = trade['Put/Call'] if trade['Put/Call'] else None
        self.price = float(trade['TradePrice'])
        self.commission = float(trade['IBCommission'])
        self.cash = float(trade['NetCash'])
        self.asset = trade['AssetClass']
        self.ooc = trade['Open/CloseIndicator']
        self.multiplier = int(trade['Multiplier'])
        self.notes = trade['Notes/Codes\n']
        if self.notes and self.notes[-1] == '\n': self.notes = self.notes[0:-1]
        self.raw_id = trade['raw_id']
        self.port = trade['port']
        if '_id' in trade.keys(): self._id = trade['_id']

    @classmethod
    def new(cls, raw):
        """ Routine to create a new trade. Return the trade """
        # Move _id and port down in 'trade' to make class creation easy
        raw.trade['raw_id'] = raw._id 
        raw.trade['port'] = raw.port
        trade = cls(raw.trade)
        return trade.create()

    def __str__(self):
        return str(vars(self))

        
# Private functions
def _parse(symbol: str) -> str:
    stock = symbol.split(' ')[0]
    if stock[-1].isalpha(): return stock
    return stock[0:-1]
    
