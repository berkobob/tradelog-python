import requests, json

# querystring = {"region":"GB","lang":"en","symbols":"AAPL%2CGOOG%2CAV.L"}

class Prices:
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/get-quotes"
    querystring = {"region":"GB","lang":"en"}
    headers = {
        'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
        'x-rapidapi-key': "eb592d6f74msh1fdca4824b15878p1afbc3jsn261d349004d2"
        }

    @classmethod
    def price(cls, positions):
        symbols = ""
        for position in positions:
            if position.stock == 'BRK': position.stock = 'BRK-B'
            symbols += position.stock + ','

        # cls.querystring['symbols'] = symbols
        # response = requests.request("GET", cls.url, headers=cls.headers, params=cls.querystring)
        # x = json.loads(response.text)
        # with open('data/test.json', 'w') as file:
        #     json.dump(x, file)

        with open('data/test.json') as file:
            data = json.load(file)

        results = data['quoteResponse']['result']
        message = []

        for result in results:
            position = [pos for pos in positions if pos.stock == result['symbol']][0]
            message.append({
                "stock": position.stock,
                "price": result["regularMarketPrice"],
                "cost": position.proceeds / position.quantity
            })
        
        return message

