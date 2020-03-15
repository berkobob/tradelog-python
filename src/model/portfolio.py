from src.model.model import Model
from src.common.result import Result

class Portfolio(Model):
    """ A list of stock with share and option positions """
    collection = "portfolios"

    def __init__(self, port):
        self.name = port['name']
        self.description = port['description']
        if '_id' in port.keys():
            self._id = port['_id']

    def commit(self, raw):
        print(raw)
        print(self)
        # remember to update the raw record with this port name
        return Result(success=True)