from src.model.raw import Raw
from src.model.position import Position
from src.model.stock import Stock
from src.model.portfolio import Portfolio
import unittest
from consts import *

class TestFourthTrade(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('Buy to close May 13 $20p on INTC')

    # Commit trade
    def testF_write_INTC_put(self):
        id = Raw.read({'trade.TradeDate': '20130517'})._id
        self.assertIsNotNone(id)
        result = Log.commit_raw_trade(id, port)
        self.assertTrue(result.success)

    # Check Position
    def testG_check_position(self):
        position = Position.read({'port': port, 'symbol': 'INTC  130518P00020000'})
        self.assertIsNotNone([position], f"Could not find {position} position")
        self.assertEqual(position.proceeds, 62.0, "Wrong proceeds")
        self.assertEqual(position.risk_per, -2000.0, "Wrong risk_per")
        self.assertAlmostEqual(position.risk, 0.031, msg="Wrong risk")

    # Check Stock
    def testH_check_stock(self):
        stock = Stock.read({'port': port, 'stock': 'INTC'})
        self.assertIsNotNone(stock, "Failed to find stock")
        self.assertEqual(stock.open, 0)
        self.assertEqual(stock.closed, 1)
        self.assertEqual(stock.proceeds, 62)
        self.assertEqual(stock.risk, 0.0)

    #Check portfolio
    def testI_check_portfolio(self):
        portfolio = Portfolio.read({'name': port})
        self.assertIsNotNone(portfolio)
        self.assertEqual(portfolio.stocks, 2)
        self.assertEqual(portfolio.open, 0)
        self.assertEqual(portfolio.closed, 2)
        self.assertEqual(portfolio.proceeds, 212)
        self.assertEqual(portfolio.risk, 0)

    @classmethod
    def tearDownClass(cls):
        print('\nFourth trade succesfully committed')


if __name__ == '__main__':
    unittest.main()