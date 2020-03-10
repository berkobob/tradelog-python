import json

class Trade:
    """ buying or selling a stock or option """
    def __init__(self, trade):
        self.trade = trade

    def __repr__(self):
        return self.trade

    def __str__(self):
        return json.dumps(self.trade)