import unittest 
from consts import *
from config import testing
from src.common.database import DB

db = 'testing'

filename = 'test.csv'
raw_count = 33

class Test_create_port_and_load_raw(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        DB.connect(testing.DB_URL, db)
        DB.drop(db)
        print(f'\nSetting up test suite by deleting {db} database\n')
        
    def test1_create_portfolio(self):
        result = Log.get_ports()
        self.assertTrue(result.success)
        self.assertFalse(result.message)
        result = Log.create_portfolio({'name': port,
                                        'description': 'A portfolio for testing'
                                        })
        self.assertTrue(result.success)
        result = Log.get_ports()
        self.assertTrue(result.success)
        self.assertEqual(len(result.message), 1)

    def test2_load_raw_trades(self):
        result = Log.load_trades_from(filename)
        self.assertTrue(result.success,
                        f"Failed to load raw trades {filename}")
        self.assertEqual(result.message, raw_count,
                        "Not all the raw trades we successfully written")   

    @classmethod
    def tearDownClass(cls):
        print('\nSetup database and raw trades. Ready for first trade')