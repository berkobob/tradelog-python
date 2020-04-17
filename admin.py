import sys, json
from os import environ
from pymongo import MongoClient
from src.model.portfolio import Portfolio
from src.model.raw import Raw
from src.common.database import DB

def backup(db):
    client = MongoClient(db_url)
    print(client.admin.command('ping'))
    db = client[db]

    ports = [{'name': port['name'], 'description': port['description']} for port in db['portfolios'].find()]
    with open('portfolios.json', 'w') as f:
        json.dump([{'name': port['name'], 'description': port['description']} for port in db['portfolios'].find()], f)
    print(f'Successfully backedup {len(ports)} portfolios')

    trades = [{'trade': raw['trade'], 'port': raw['port']} for raw in db['raw'].find({'port': {'$ne': None}})]
    with open('trades.json', 'w') as f:
        json.dump(trades, f)
    print(f'Successfully backedup {len(trades)} trades')

    raw = [{'trade': raw['trade']} for raw in db['raw'].find({'port': None})]
    with open('raw.json', 'w') as f:
        json.dump(raw, f)
    print(f'Successfully backedup {len(raw)} raw trades')


def restore(db):
    DB.connect(db_url, db)
    DB.drop(db)

    with open('portfolios.json', 'r') as f:
        portfolios = json.load(f)

    for portfolio in portfolios:
        try:
            x = Portfolio.new(portfolio)
        except Exception as e:
            print(e)
        else:
            print(x)

    with open('trades.json', 'r') as f:
        trades = json.load(f)
        trades.sort(key=lambda i: (i['port'], i['trade']['TradeDate']))

    name = " "
    for record in trades:
        trade = Raw.new(record['trade'])
        if name != record['port']: 
            port = Portfolio.get(record['port'])
            name = port.name
        print(port.commit(trade))

    with open('raw.json', 'r') as f:
        raw = json.load(f)

    [print(Raw.new(r)) for r in raw]

def setup():
    from src.model.user import User

    DB.connect('mongodb://mongo:27017', 'production')
    DB.drop('production')
    b = User.new({
        '_id': "105728265192260536412",
        "email": "alever",
        "name": "antoine",
        "profile_pic": "https://lh3.googleusercontent.com/a-/AOh14Gjhv_yDJ7H9pzKt-Ys_qpo3z1arP8b2oonY9bIGEw"
    })
    print(b)
    print(DB.ping())


if __name__ == '__main__':

    db_url = environ.get('DB_URL')
    print(db_url)

    if len(sys.argv) == 3:

        if sys.argv[1] == 'backup': backup(sys.argv[2])
        elif sys.argv[1] == 'restore': restore(sys.argv[2])
        elif sys.argv[1] == 'setup': setup()
        else: print('backup or restore only')

    else:
        print("Expecting two arguments: admin.py [backup|restore] database_name")

