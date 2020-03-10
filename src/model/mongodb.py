from pymongo import MongoClient

class DB:
    """ The database API """
    db = None

    @classmethod
    def connect(cls, URL, env):
        # mongo = MongoClient(URL)
        try:
            cls.db = MongoClient(URL)[env]
        except Exception as e:
            return {'success': False, 'message': str(e), 'severity': 'ERROR'}
        return {'succcess': True}
        
    @classmethod
    def add_raw_trade(cls, trade):
        try:
            cls.db.raw_trades.insert_one(trade)
        except Exception as e:
            return {'success': False, 'message': str(e), 'severity': 'ERROR'}
        return {'succcess': True}

    @classmethod
    def new_port(cls, port):
        try: 
            cls.db.portfolios.insert_one(port)
        except Exception as e:
            return {'success': False, 'message': str(e), 'severity': 'ERROR'}
        return {'success': True}

    @classmethod
    def get_portfolios(cls):
        return [port for port in cls.db.portfolios.find()]