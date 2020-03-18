from src.model.model import Model
from src.common.database import DB

class Raw(Model):
    """ buying or selling a stock or option """
    collection = 'raw' 

    def __init__(self, trade):
        if 'trade' in trade.keys(): 
            self.trade = trade['trade']
        else: 
            self.trade = trade
        self.port = trade['port'] if 'port' in trade.keys() else None
        if '_id' in trade.keys(): self._id = trade['_id']

    def commit(self, port):
        self.port = port
        return self.update({'port': port})