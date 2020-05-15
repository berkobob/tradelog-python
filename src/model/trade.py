from src.model.model import Model
from datetime import datetime
from bson.objectid import ObjectId
from src.common.exception import AppError

class Trade(Model):
    """ buying or selling a stock or option """
    collection = "trades"

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
        # self.risk = trade['risk']

    @classmethod
    def new(cls, raw):
        """ Routine to create a new trade. Return the trade """
        # Move _id and port down in 'trade' to make class creation easy
        try:
            raw.trade['_id'] = ObjectId()
            raw.trade['raw_id'] = raw._id 
            raw.trade['port'] = raw.port
            raw.trade['date'] = datetime.strptime(raw.trade['TradeDate'], "%Y%m%d") if 'TradeDate' in raw.trade.keys() else datetime.strptime(raw.trade['Date'], '%d/%m/%y')
            raw.trade['bos'] = raw.trade['Buy/Sell'] # if 'Buy/Sell' in raw.trade.keys() else raw.trade['Shares']
            raw.trade['quantity'] = int(raw.trade['Quantity']) # if 'Quantity' in raw.trade.keys() else int(raw.trade['Shares'])
            raw.trade['symbol'] = raw.trade['Symbol'] # if 'Symbol' in raw.trade.keys() else raw.trade['TIDM']
            raw.trade['stock'] = raw.stock
            if 'Expiry' in raw.trade.keys() and raw.trade['Expiry']:
                if '/' in raw.trade['Expiry']:
                    raw.trade['expiry'] = datetime.strptime(raw.trade['Expiry'], "%d/%m/%Y")
                else:
                    raw.trade['expiry'] = datetime.strptime(raw.trade['Expiry'], "%Y%m%d")
            else: raw.trade['expiry'] = None
            raw.trade['strike'] = float(raw.trade['Strike']) if raw.trade['Strike'] else None
            raw.trade['poc'] = raw.trade['Put/Call'] if raw.trade['Put/Call'] else None
            raw.trade['price'] = float(raw.trade['TradePrice'])
            raw.trade['proceeds'] = float(raw.trade['Proceeds'])
            raw.trade['commission'] = float(raw.trade['IBCommission'])
            raw.trade['cash'] = float(raw.trade['NetCash'])
            raw.trade['asset'] = raw.trade['AssetClass']
            raw.trade['ooc'] = raw.trade['Open/CloseIndicator']
            raw.trade['multiplier'] = int(raw.trade['Multiplier'])
            raw.trade['notes'] = raw.trade['Notes/Codes']
        except Exception as e:
            raise AppError(e)
        else:
            raw.commit(raw.port)
            return cls(raw.trade).create()

    def build_result(self, pos, risk_per, stocks=0, open=0, closed=0):
        return {
            'stock': self.stock,
            'stocks': stocks,
            'open': open,
            'closed': closed,
            'proceeds': 0,
            'commission': 0,
            'cash': 0,
            'risk': self.quantity * risk_per,
            'pos': pos
        }
    
    def risk(self):
        if self.asset == 'STK':
            if self.quantity > 0: # Assume long as short is infinite risk
                return self.price * self.multiplier

        elif self.asset == 'OPT':
            if self.quantity > 0: # Long
                return self.price * self.multiplier
            elif self.quantity < 0: # Short
                if self.poc == 'P':
                    return -self.strike * self.multiplier

        return 0

    def to_json(self):
        json = vars(self)
        json['_id'] = str(self._id)
        json['raw_id'] = str(self.raw_id)
        return json