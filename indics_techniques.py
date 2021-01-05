from tradingview_ta import TA_Handler, Interval
import os

i = 0
def cls():
    os.system('cls' if os.name=='nt' else 'clear')

cls()


print("Bienvenue sur Tradyglo v.BETA")
while i == 0 :
    symbol = input("entreprise symbole > ")
    exchange = input("place bourisère > ")
    country = input("pays > ")

    print("-"*100)
    print("Résultats analyses techniques",symbol,":")


    _object = TA_Handler()
    _object.set_symbol_as(symbol)
    _object.set_exchange_as_crypto_or_stock(exchange)
    _object.set_screener_as_stock(country)
    _object.set_interval_as(Interval.INTERVAL_1_DAY)
    test = _object.get_analysis().summary

    print("1 jour >",test)

    _object.set_interval_as(Interval.INTERVAL_1_WEEK)
    test = _object.get_analysis().summary
    print("1 sem >",test)

    _object.set_interval_as(Interval.INTERVAL_1_MONTH)
    test = _object.get_analysis().summary
    print("1 mois >",test)
    print("\n")






#cls()

