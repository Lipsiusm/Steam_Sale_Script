import requests
import json
import datetime
import time
from games import Game
from bs4 import BeautifulSoup as bs
#from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By

def send_info(data):
    
    with open("../bot_info.json", "r") as webhook_file:
        bot_info  = json.load(webhook_file)

    DIG_WEBHOOK = bot_info['DIG_WEBHOOK']
    SMP_WEBOOK = bot_info['SMP_WEBOOK']
    
    sales = ''

    for sale in data:
        sales = sales + f'{sale}\n'

    #embed the sales for a good looking output
    DIG_data = {
        "username": "SteamBot",
        "embeds": [
            {
                "title": "CDN Steam Sales",
                "description": sales,
                "color": "16704809",
            }
        ],
    }

    requests.post(DIG_WEBHOOK, data = json.dumps(DIG_data), headers={'Content-Type':'application/json'})
    #requests.post(SMP_WEBOOK, data = json.dumps(DIG_data), headers={'Content-Type':'application/json'})

def top_sellers():

    #nabbin up them current specials
    #STORE_URL= 'https://store.steampowered.com/search/?sort_by=Reviews_DESC&supportedlang=english&specials=1&filter=topsellers'
    STORE_URL = 'https://store.steampowered.com/search/?os=win&supportedlang=english&specials=1&hidef2p=1&filter=globaltopsellers&ndl=1'
    return_games = []
    return_list = []
    check_url_status = requests.get(STORE_URL)
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(STORE_URL)

    #if the website is up, nab the sales
    #otherwise send an error message to Discord

    if check_url_status.status_code == 200:
        
        feed = requests.get(STORE_URL)
        soup = bs(driver.page_source, 'html.parser')
        find_games = soup.find_all(class_=['title', "col search_discount responsive_secondrow", 'col search_price discounted responsive_secondrow'])
        games = []

        #cut tag info off the items in the list
        for i in range (len(find_games)):
            find_games[i] = find_games[i].get_text()
            find_games[i] = find_games[i].strip()
            
            if len(find_games[i])== 0:

                #blank entry being printed, remove the last addition
                games.remove(games[len(games)-1])

            if len(find_games[i]) > 0:
                games.append(find_games[i])

        for i in games:
            title = games.pop(0)
            pct = games.pop(0)

            #stripping the CDN dollar characters to save character spaces
            cost_before_strip = games.pop(0)
            cost = cost_before_strip[-5:]


            new_game = Game(pct, cost, title)
            #print("Title is: " + title + " Cost is: " + cost + " Discount is " + pct)
            if new_game not in return_games:
                return_games.append(new_game)

        for i in return_games:
            return_list.append(f'{i.get_title()} - {i.get_cost()} ({i.get_discount()} off)')


        return return_list
    else:
        return "Steam website is down"
    driver.quit()
    
def main ():
    contine_trying = True

    #keep trying to post games, but with cpu sharing on aws sometimes it doesn't work
    # so we're going to try every 15 minutes
    while contine_trying:
        try:
            data = top_sellers()
            send_info(data)
            
        except Exception as e:
            with open ("./SteamBot.log", "a") as logfile:
                time = datetime.datetime.now()
                logfile.write("Exception occured at: " + str(time))
                logfile.write(str(e))

                #wait 5 minutes and try again
                time.sleep(300)
        else:
            print("Games posted successfully")
            contine_trying = False

#if this application was run directly, run main
if __name__ == "__main__":
    main()
