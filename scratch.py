from src.common.database import DB
from src.model.portfolio import Portfolio

DB.connect('mongodb+srv://tradelog:tradelog@cluster0-4ov7h.mongodb.net/?retryWrites=true&w=majority', 'development')

# port = Portfolio({'name': 'Antoine', 'description': 'rules'})
# print(port.create())

for port in Portfolio.all():
    print(type(port), port)

# print(type(port))
# class Test:
#     def __init__(self):
#         self.first = "First"
#         self.second = "Second"

#     def __str__(self):
#         return str(vars(self))

#     def __repr__(self):
#         return vars(self)

# test = Test()

# print(type(test), test)