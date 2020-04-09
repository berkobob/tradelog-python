from src.model.raw import Raw
from src.model.position import Position
from src.model.stock import Stock
from src.model.portfolio import Portfolio
import unittest
from consts import *

class TestFirstTrade(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('Write April 13 $57.50p on AXP')

    def test3_write_AXP_put(self):
        # Commit trade
        id = Raw.read({'trade.TradeDate': '20130118'})._id
        # id = id._id
        self.assertIsNotNone(id)
        result = Log.commit_raw_trade(id, port)
        self.assertTrue(result.success)

    # Check Position
    def test4_check_position(self):
        position = Position.read({'port': port, 'symbol': 'AXP   130420P00057500'})
        self.assertIsNotNone([position], f"Could not find {position} position")
        self.assertEqual(position.proceeds, 150.0, "Wrong proceeds")
        self.assertEqual(position.risk_per, -5750.0, "Wrong risk_per")
        self.assertEqual(position.risk, 5750.0, "Wrong risk")

    # Check Stock
    def test5_check_stock(self):
        stock = Stock.read({'port': port, 'stock': 'AXP'})
        self.assertIsNotNone(stock, "Failed to find stock")
        self.assertEqual(stock.open, 1)
        self.assertEqual(stock.closed, 0)
        self.assertEqual(stock.proceeds, 0)
        self.assertEqual(stock.risk, 5750)

    #Check portfolio
    def test6_check_portfolio(self):
        portfolio = Portfolio.read({'name': port})
        self.assertIsNotNone(portfolio)
        self.assertEqual(portfolio.stocks, 1)
        self.assertEqual(portfolio.open, 1)
        self.assertEqual(portfolio.closed, 0)
        self.assertEqual(portfolio.proceeds, 0)
        self.assertEqual(portfolio.risk, 5750)

    @classmethod
    def tearDownClass(cls):
        print('\nFirst trade succesfully committed')


if __name__ == '__main__':
    unittest.main()