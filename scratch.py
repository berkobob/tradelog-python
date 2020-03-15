from src.common.database import DB
from src.model.portfolio import Portfolio
from src.model.raw import Raw
from bson.objectid import ObjectId
from src.controller.tradelog import get_raw_trades

DB.connect('mongodb+srv://tradelog:tradelog@cluster0-4ov7h.mongodb.net/?retryWrites=true&w=majority', 'development')

