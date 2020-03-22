from src.common.database import DB
from src.model.portfolio import Portfolio
from src.model.stock import Stock

DB.connect('mongodb+srv://tradelog:tradelog@cluster0-4ov7h.mongodb.net/?retryWrites=true&w=majority', 'development')

result = Portfolio.get('Antoine')
port = result.message
# print(port)

print(port.get_positions('ORCL'))