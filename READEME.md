# Tradelog

A client server type app with a web, desktop and command line interface.

## Objectives

1. How much made per trade
2. What trades are open
3. Calc total risk

## Definitions

Trade | buy or sell something
Position | size & value
stock | a list of share trades and a list of options trades
Portfolio | a list of stocks
TradeLog | a list of portfolios

## Messaging?

View - only view can flash message

Controller - raises error or passes from model

Model - can only raise error 


[uwsgi]
http = :8080
https = :8443,fullchain.pem,privkey.pem,HIGH
wsgi-file = src/app.py
callable = app
master = true
processes = 4
threads = 8
memory-report = true
stats = stats.sock
plugins = router_redirect
route-if-not = equal:${HTTPS};on redirect-permanent:https://${HTTP_HOST}${REQUEST_URI}