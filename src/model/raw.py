from src.model.model import Model
from bson.objectid import ObjectId

class Raw(Model):
    """ This represents the raw data from the .csv import """
    collection = 'raw' 

    def __init__(self, trade):
        self._id = trade['_id']
        self.trade = trade['trade']
        self.port = trade['port']

    @classmethod
    def new(cls, trade):
        return cls({
            '_id': ObjectId(),
            'trade': trade,
            'port': None
        }).create()

    def commit(self, port):
        self.port = port
        return self.update({'port': port})