from src.common.database import DB
from src.model.portfolio import Portfolio
from src.model.stock import Stock

x, y, z = DB.connect('mongodb+srv://tradelog:tradelog@cluster0-4ov7h.mongodb.net/?retryWrites=true&w=majority', 'development')

print(x, y, z)