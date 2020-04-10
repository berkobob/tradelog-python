import sys, json
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

    trades = [{'trade': raw['trade'], 'port': raw['port']} for raw in db['raw'].find()]
    with open('raw.json', 'w') as f:
        json.dump(trades, f)
    print(f'Successfully backedup {len(trades)} raw trades')


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

    with open('raw.json', 'r') as f:
        raw = json.load(f)
        raw.sort(key=lambda i: (i['port'], i['trade']['TradeDate']))

    name = ""
    for record in raw:
        raw = Raw.new(record['trade'])
        if name != record['port']: 
            port = Portfolio.get(record['port'])
            name = port.name
        result = port.commit(raw)
        print(result)

if __name__ == '__main__':

    if len(sys.argv) == 3:

        if sys.argv[1] == 'backup': backup(sys.argv[2])
        elif sys.argv[1] == 'restore': restore(sys.argv[2])
        else: print('backup or restore only')

    else:
        print("Expecting two arguments: admin.py [backup|restore] database_name")
        restore('test')

