from bs4 import BeautifulSoup
import urllib.request
import sys
import sqlite3
from tradingview_ta import TA_Handler, Interval
import os
import re




def f_start():
    actual_date = "17-11" #mettre jour-month, il vas remettre dans l'odre
    total_gains_pertes = 0


    with connexion: 
        connexion.execute("""CREATE TABLE IF NOT EXISTS trading_positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        companie TEXT,
        date DATE,
        action TEXT,
        result TEXT,
        gains_pertes INTEGER,
        objectifs TEXT,
        status TEXT,
        synthese TEXT,
        author TEXT,
        url TEXT
        );""")

    nb_pages = input("Nombres de pages à récupérer > ")
    try:
        nb_pages = int(nb_pages)
    except:
        nb_pages = 0

    list_links = []

    for i in range(0,nb_pages):
        i += 1
        i = str(i)
        list_links.append("https://www.zonebourse.com/analyse-bourse/strategies-trading-actions/?p5=" + i)
    print(list_links)

    baselink = "https://www.zonebourse.com"

    for link in list_links :

        pagelink = urllib.request.urlopen(link)
        soup = BeautifulSoup(pagelink, 'html.parser')
        news = soup.find('table', attrs={'class': 'home_strat'})

        for new in news:
            companie = "Null"
            status = "Null"
            action = "Null"
            objectifs = "Null"
            result = "Null"
            synthese = "Null"
            author = "Null"
            url = "Null"
            date = "Null"
            id_same_url = 0
            actual_id = 0
            already_exist = False
            

            try :
                news = list(news)
                new = list(new)
                find_action = new[3]
                find_action = list(find_action)
                action = find_action[1].text.strip()

                all_infos = new[1]
                all_infos = list(all_infos)
                all_infos = all_infos[1]
                all_infos = list(all_infos)

                companie = all_infos[1].text
                companie = companie.strip()

                date = companie[-5:]
                for letter in date:
                    if letter == ":":
                        date = actual_date
                date = "2020-" + date[-2:] + "-" + date[:2]

                companie =  companie[0:-8]

                status = all_infos[3].text
                status = status.strip()

                url = all_infos[3]
                url = list(url)
                url = url[1]
                url = url.find('a')
                url = url['href']
                url = baselink + url

                #----------------------------------------------- 2 eme page -----------------------------------------------#
                pagelink2 = urllib.request.urlopen(url)
                soup2 = BeautifulSoup(pagelink2, 'html.parser')


                result = soup2.find('span', attrs={'style': 'vertical-align: middle;'}).text

                objectifs = soup2.find('td', attrs={'style': 'padding: 0px 0px 10px 0px; text-align: left;'}).text
                objectifs = objectifs.strip()

                position_barre = objectifs.find('|')
                int_entree = objectifs[position_barre-12:position_barre-1]
                int_entree = re.sub('[)(azertyuiopmlkjhgfdsqwxcvbnAZERTYUIOPMLKJHGFDSQWXCVBNéàèê€£¥%$:]', '', int_entree).strip()
                int_entree = float(int_entree) 
                int_entree_fixe = int_entree
                int_entree = int(int_entree / int_entree * 10000)
                objectifs2 = objectifs[position_barre+1:]

                position_barre = objectifs2.find('|')
                int_objectif = objectifs2[position_barre-12:position_barre-1]
                int_objectif = re.sub('[)(azertyuiopmlkjhgfdsqwxcvbnAZERTYUIOPMLKJHGFDSQWXCVBNéàèê€£¥%$:]', '', int_objectif).strip()
                int_objectif = float(int_objectif)
                int_objectif = int(int_objectif / int_entree_fixe * 10000)
                int_objectif = int_objectif - int_entree
                objectifs2 = objectifs2[position_barre+1:]

                position_barre = objectifs2.find('|')
                int_stop = objectifs2[position_barre-12:position_barre-1]
                int_stop = re.sub('[)(azertyuiopmlkjhgfdsqwxcvbnAZERTYUIOPMLKJHGFDSQWXCVBNéàèê€£¥%$:]', '', int_stop).strip()
                int_stop = float(int_stop)
                int_stop = int(int_stop / int_entree_fixe * 10000)
                int_stop = int_stop - int_entree
                objectifs2 = objectifs2[position_barre+1:]


                if result == "En cours" or result == "En attente":
                    gains_pertes = 0
                elif result == "Stop atteint":
                    gains_pertes = int_stop
                    gains_pertes = gains_pertes / 2921 * 100
                    gains_pertes = round(gains_pertes,2)
                elif result == "Objectif atteint":
                    gains_pertes = int_objectif
                    gains_pertes = gains_pertes / 2921 * 100
                    gains_pertes = round(gains_pertes,2)
                else:
                    gains_pertes = 0

                if action == "VENTE":
                    gains_pertes *= -1




                synthese = soup2.find('ul', attrs={'class': 's_and_w'}).text

                author = soup2.find('span', attrs={'itemprop': 'name'}).text

                c.execute(f"SELECT id FROM trading_positions where url = '{url}';")
                try:
                    id_same_url = c.fetchone()[0]
                except:
                    id_same_url = None


                if id_same_url is not None:
                    already_exist = True


                if already_exist is False:
                    with connexion:
                        c.execute("INSERT INTO trading_positions (companie, status, action, objectifs, result, synthese, author, url, date, gains_pertes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (companie, status, action, objectifs, result, synthese, author, url, date, gains_pertes))
                        c.execute(f"SELECT id FROM trading_positions where url = '{url}';")
                        actual_id = c.fetchone()[0]
                    print("-> NEW : insert ok > id >", actual_id,"-", companie,"-",action,"-",result)


                if already_exist:
                    with connexion:
                        c.execute(f"UPDATE trading_positions SET companie = ?, status = ?, action = ?, objectifs = ?, result = ?, synthese = ?, author = ?, url = ?, gains_pertes = ?, date = ? WHERE id = {id_same_url}", (companie, status, action, objectifs, result, synthese, author, url, date, gains_pertes))
                        c.execute(f"SELECT id FROM trading_positions where url = '{url}';")
                        actual_id = c.fetchone()[0]            
                    print("update ok > id >", actual_id,"-", companie,"-",action,"-",result)

                total_gains_pertes += gains_pertes
                print("Gains ou pertes > ", gains_pertes)
                print("Total > ", total_gains_pertes)
                print("-----------------------------------------------")

            except :
                pass
        print("-"*100)

    #seconde partie on check si les données qui n'ont pas de result peuvent être update -----------------------------------------------------------------------
    




def f_infos():

    id_search = 0
    infos = "Null"

    try:
        id_search = int(command[7:])
    except:
        id_search = 0

    with connexion: 
        try :
            c.execute(f"SELECT * FROM trading_positions where id = {id_search};")
            infos = c.fetchone()
            print("id >",infos[0],"\ncompanie & date >",infos[1],"\nstatus >",infos[2],"\naction >",infos[3],"\nobjectifs >",infos[4],"\nsynthèse >",infos[6],"\nauthor >",infos[7],"\nresult >",infos[5])
            print("-"*100)
        except :
            print("L'ID :",id_search,"n'existe pas")


def t_infos():







    symbol = input("entreprise symbole :\n> ")
    exchange = input("place bourisère :\n> ")
    country = input("pays: \n> ")


    print("Résultats analyses techniques",symbol,":")

    try :
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
        print("-"*100)
    except:
        print("ERREUR > une ou plusieures données sont érronées.")





# COMMANDS ------------------------------------

connexion = sqlite3.connect("trading_positions.db")
c = connexion.cursor()
infinity = True

os.system('cls' if os.name=='nt' else 'clear')

list_commands="""Commandes analyses fondamentales:
    f start
    f infos [id]
Commandes analyses techniques:
    t infos
Autre:
    exit"""

print("-"*100)
print("                                 Bienvenue sur Tradyglo v2.0 !")
print("-"*100)
print(list_commands)
print("-"*100)



while infinity:



    command = input(">>> ")


    if command[:7] == "f infos":
        f_infos()


    elif command[:7] == "f start":
        f_start()


    elif command[:7] == "t infos":
        t_infos()


    elif command[:4] == "exit":
        sys.exit()


    else:
        print(list_commands)
        print("-"*100)





    total = 0
    values = []

    with connexion: 
        connexion.execute("""CREATE TABLE IF NOT EXISTS trading_positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        companie TEXT,
        date DATE,
        action TEXT,
        result TEXT,
        gains_pertes TEXT,
        objectifs TEXT,
        status TEXT,
        synthese TEXT,
        author TEXT,
        url TEXT
        );""")

    c.execute("SELECT gains_pertes FROM trading_positions order by date;")
    gains_pertes = c.fetchall()


    for element in gains_pertes:
        element = list(element)
        element = int(element[0])
        if element != 0:
            total += element
            print(total)
            values.append(total)
    print(values)