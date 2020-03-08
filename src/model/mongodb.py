from pymongo import MongoClient

class DB:
    """ The database API """
    def __init__(self, URL, env):
        mongo = MongoClient(URL)
        self.db = mongo[env]


    # def dbtest(self):
    #     for trade in self.test.find():
    #         print(trade)

    # def getOne(self):
    #     return self.test.find_one()
