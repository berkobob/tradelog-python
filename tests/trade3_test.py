from src.model.raw import Raw
from src.model.position import Position
from src.model.stock import Stock
from src.model.portfolio import Portfolio
import unittest
from consts import *

class TestThirdTrade(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('Buy to close April 13 $57.50p on AXP')

    def testB_close_AXP_put(self):
        # Commit trade
        id = Raw.read({'trade.TradeDate': '20130419'})._id
        self.assertIsNotNone(id)
        result = Log.commit_raw_trade(id, port)
        self.assertTrue(result.success)

    # Check Position
    def testC_check_position(self):
        position = Position.read({'port': port, 'symbol': 'AXP   130420P00057500'})
        self.assertIsNotNone([position], f"Could not find {position} position")
        self.assertEqual(position.proceeds, 150.0, "Wrong proceeds")
        self.assertEqual(position.risk_per, -5750, "Wrong risk_per")
        self.assertAlmostEqual(position.risk, 0.0260869, places=3, msg="Wrong risk")

    # Check Stock
    def testD_check_stock(self):
        stock = Stock.read({'port': port, 'stock': 'AXP'})
        self.assertIsNotNone(stock, "Failed to find stock")
        self.assertEqual(stock.open, 0)
        self.assertEqual(stock.closed, 1)
        self.assertEqual(stock.proceeds, 150)
        self.assertEqual(stock.risk, 0)

    #Check portfolio
    def testE_check_portfolio(self):
        portfolio = Portfolio.read({'name': port})
        self.assertIsNotNone(portfolio)
        self.assertEqual(portfolio.stocks, 2)
        self.assertEqual(portfolio.open, 1)
        self.assertEqual(portfolio.closed, 1)
        self.assertEqual(portfolio.proceeds, 150.0)
        self.assertEqual(portfolio.risk, 2000.0)

    @classmethod
    def tearDownClass(cls):
        print('\nThird trade succesfully committed')


if __name__ == '__main__':
    unittest.main()