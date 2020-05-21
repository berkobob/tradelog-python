from src.model.price import Price
from src.controller.tradelog import TradeLog as Log

class Prices:
    @classmethod
    def price(cls, positions):
        prices = Price.read({}, True)
        message = []

        for position in positions:
            if 'shares' in position.position:
                price = [price.price for price in prices if price._id == position.stock][0]
                percent = (price-position.risk_per) / position.risk_per if position.risk_per != 0 else 0
                message.append({
                    'stock': position.stock,
                    'cost': position.risk_per,
                    'price': price,
                    'percent': percent,
                    'value': price * position.quantity
                })

        return message

    @classmethod
    def prices(cls, ports):
        message = []
        for port in ports:
            positions = [position for position in Log.get_open_positions(port.name).message]
            message.append({
                'port': port.name,
                'value': sum(price['price'] for price in cls.price(positions))
            })
        return message