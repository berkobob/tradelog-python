from src.model.model import Model
from bson.objectid import ObjectId

class Raw(Model):
    """ This represents the raw data from the .csv import """
    collection = 'raw' 

    def __init__(self, _id, trade, port):
        self._id = _id
        self.trade = trade
        self.port = port

    @classmethod
    def new(cls, trade):
        return cls(**{
            '_id': ObjectId(),
            'trade': trade,
            'port': None
        }).create()

    def commit(self, port):
        self.port = port
        return self.update({'port': port})