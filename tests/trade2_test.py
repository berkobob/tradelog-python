from src.model.raw import Raw
from src.model.position import Position
from src.model.stock import Stock
from src.model.portfolio import Portfolio
import unittest
from consts import *

class TestSecondTrade(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('Write May 13 $20p on INTC')

    # Commit trade
    def test7_write_INTC_put(self):
        id = Raw.read({'trade.TradeDate': '20130206'})._id
        self.assertIsNotNone(id)
        result = Log.commit_raw_trade(id, port)
        self.assertTrue(result.success)

    # Check Position
    def test8_check_position(self):
        position = Position.read({'port': port, 'symbol': 'INTC  130518P00020000'})
        self.assertIsNotNone([position], f"Could not find {position} position")
        self.assertEqual(position.proceeds, 62.0, "Wrong proceeds")
        self.assertEqual(position.risk_per, -2000.0, "Wrong risk_per")
        self.assertEqual(position.risk, 2000.0, "Wrong risk")

    # Check Stock
    def test9_check_stock(self):
        stock = Stock.read({'port': port, 'stock': 'INTC'})
        self.assertIsNotNone(stock, "Failed to find stock")
        self.assertEqual(stock.open, 1)
        self.assertEqual(stock.closed, 0)
        self.assertEqual(stock.proceeds, 0)
        self.assertEqual(stock.risk, 2000)

    #Check portfolio
    def testA_check_portfolio(self):
        portfolio = Portfolio.read({'name': port})
        self.assertIsNotNone(portfolio)
        self.assertEqual(portfolio.stocks, 2)
        self.assertEqual(portfolio.open, 2)
        self.assertEqual(portfolio.closed, 0)
        self.assertEqual(portfolio.proceeds, 0)
        self.assertEqual(portfolio.risk, 7750)

    @classmethod
    def tearDownClass(cls):
        print('\nSecond trade succesfully committed')


if __name__ == '__main__':
    unittest.main()