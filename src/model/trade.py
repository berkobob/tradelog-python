from src.model.model import Model
from datetime import datetime
from bson.objectid import ObjectId
from src.common.exception import AppError

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
            raw.trade['date'] = datetime.strptime(raw.trade['TradeDate'], "%Y%m%d")
            raw.trade['bos'] = raw.trade['Buy/Sell']
            raw.trade['quantity'] = int(raw.trade['Quantity'])
            raw.trade['symbol'] = raw.trade['Symbol']
            raw.trade['stock'] = _parse(raw.trade['Symbol'])
            raw.trade['expiry'] = datetime.strptime(raw.trade['Expiry'], "%d/%m/%Y") if raw.trade['Expiry'] else None
            raw.trade['strike'] = float(raw.trade['Strike']) if raw.trade['Strike'] else None
            raw.trade['poc'] = raw.trade['Put/Call'] if raw.trade['Put/Call'] else None
            raw.trade['price'] = float(raw.trade['TradePrice'])
            raw.trade['proceeds'] = float(raw.trade['Proceeds'])
            raw.trade['commission'] = float(raw.trade['IBCommission'])
            raw.trade['cash'] = float(raw.trade['NetCash'])
            raw.trade['asset'] = raw.trade['AssetClass']
            raw.trade['ooc'] = raw.trade['Open/CloseIndicator']
            raw.trade['multiplier'] = int(raw.trade['Multiplier'])
            raw.trade['notes'] = raw.trade['Notes/Codes\n'][:-1]
        except Exception as e:
            raise AppError(e)
        else:
            return cls(raw.trade).create()

        
# Private functions
def _parse(symbol: str) -> str:
    stock = symbol.split(' ')[0]
    if stock[-1].isalpha(): return stock
    return stock[0:-1]
    
