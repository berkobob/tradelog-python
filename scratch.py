from src.common.database import DB
from src.model.portfolio import Portfolio
from src.model.stock import Stock

DB.connect('mongodb+srv://tradelog:tradelog@cluster0-4ov7h.mongodb.net/?retryWrites=true&w=majority', 'development')

port = Portfolio.read({"name": "Antoine"}).message[0]

# x = [value for stock in port.stocks for key, value in stock]
# print(x)


y = [Stock.read({'_id': x}).message[0] for x in [stock['_id'] for stock in port.stocks]]

z = [str(x) for x in[Stock.read({'_id': x}).message[0] for x in [stock['_id'] for stock in port.stocks]]]
print(z)
# z = [x for x in y]

for a in y:
    print(a)
