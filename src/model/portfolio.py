from src.model.model import Model

class Portfolio(Model):
    """ A list of stock with share and option positions """
    collection = "portfolios"

    def __init__(self, port):
        self.name = port['name']
        self.description = port['description']
        if '_id' in port.keys():
            self._id = port['_id']

