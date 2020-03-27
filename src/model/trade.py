from src.model.model import Model
from src.common.result import Result
from datetime import datetime
from bson.objectid import ObjectId

class Trade(Model):
    """ buying or selling a stock or option """
    collection = "trade"

    def __init__(self, trade):
        self._id = trade['_id']
        self.raw_id = trade['raw_id']
        self.port = trade['port']
        self.date = trade['date']
        self.bos = trade['bos']
        self.quantity = trade['quantity']
        self.symbol = trade['symbol']
        self.stock = trade['stock']
        self.expiry = trade['expiry']
        self.strike = trade['strike']
        self.poc = trade['poc']
        self.price = trade['price']
        self.proceeds = trade['proceeds']
        self.commission = trade['commission']
        self.cash = trade['cash']
        self.asset = trade['asset']
        self.ooc = trade['ooc']
        self.multiplier = trade['multiplier']
        self.notes = trade['notes']

    @classmethod
    def new(cls, raw):
        """ Routine to create a new trade. Return the trade """
        # Move _id and port down in 'trade' to make class creation easy
        try:
            raw.trade['_id'] = ObjectId()
            raw.trade['raw_id'] = raw._id 
            raw.trade['port'] = raw.port
            raw.date = datetime.strptime(raw.trade['TradeDate'], "%Y%m%d")
            raw.bos = raw.trade['Buy/Sell']
            raw.quantity = int(raw.trade['Quantity'])
            raw.symbol = raw.trade['Symbol']
            raw.stock = _parse(raw.trade['Symbol'])
            raw.expiry = datetime.strptime(raw.trade['Expiry'], "%d/%m/%Y") if raw.trade['Expiry'] else None
            raw.strike = float(raw.trade['Strike']) if raw.trade['Strike'] else None
            raw.poc = raw.trade['Put/Call'] if raw.trade['Put/Call'] else None
            raw.price = float(raw.trade['TradePrice'])
            raw.proceeds = float(raw.trade['Proceeds'])
            raw.commission = float(raw.trade['IBCommission'])
            raw.cash = float(raw.trade['NetCash'])
            raw.asset = raw.trade['AssetClass']
            raw.ooc = raw.trade['Open/CloseIndicator']
            raw.multiplier = int(raw.trade['Multiplier'])
            raw.notes = raw.trade['Notes/Codes\n']
            if raw.notes and raw.notes[-1] == '\n': raw.notes = raw.notes[0:-1]
        except Exception as e:
            return Result(success=False, message=str(e), severity='ERROR')

        trade = cls(raw.trade)
        return trade.create()

    def __str__(self):
        return str(vars(self))

        
# Private functions
def _parse(symbol: str) -> str:
    stock = symbol.split(' ')[0]
    if stock[-1].isalpha(): return stock
    return stock[0:-1]
    
