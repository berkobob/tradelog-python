from pymongo import MongoClient

class DB:
    """ The database API """

    @classmethod
    def connect(cls, URL, env):
        mongo = MongoClient(URL)
        cls.db = mongo[env]

    @classmethod
    def test(cls):
        return cls.db
        
    @classmethod
    def add_raw_trade(cls, trade):
        return cls.db.raw_trades.insert_one(trade)

    # def dbtest(self):
    #     for trade in self.test.find():
    #         print(trade)

    # def getOne(self):
    #     return self.test.find_one()
