import requests
import json
from games import Game
from bs4 import BeautifulSoup as bs
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from selenium.webdriver.common.by import By

def send_info(data):
    
    with open("../bot_info.json", "r") as webhook_file:
        bot_info  = json.load(webhook_file)

    DIG_webhook = bot_info['DIG_WEBHOOK']
    
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

    DIG_result = requests.post(DIG_webhook, data = json.dumps(DIG_data), headers={'Content-Type':'application/json'})

def top_sellers():

    #nabbin up them current specials
    #STORE_URL= 'https://store.steampowered.com/search/?sort_by=Reviews_DESC&supportedlang=english&specials=1&filter=topsellers'
    STORE_URL = 'https://store.steampowered.com/search/?os=win&supportedlang=english&specials=1&hidef2p=1&filter=globaltopsellers&ndl=1'
    return_games = []
    return_list = []
    check_url_status = requests.get(STORE_URL)
    options = FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(STORE_URL)

    #if the website is up, nab the sales
    #otherwise send an error message to Discord

    if check_url_status.status_code == 200:
        
        feed = requests.get(STORE_URL)
        soup = bs(driver.page_source, 'html.parser')
        games = soup.find_all(class_=['title', "col search_discount responsive_secondrow", 'col search_price discounted responsive_secondrow'])

        #cut tag info off the items in the list
        for i in range (len(games)):
            games[i] = games[i].get_text()
            games[i] = games[i].strip()

            #some games have multiple purchase pricing options and it frigs up my game objects when the tags are blank
            if len(games[i]) == 0:
                games[i] = "%"

        for i in games:
            title = games.pop(0)
            pct = games.pop(0)

            #stripping the CDN dollar characters to save character spaces
            cost_before_strip = games.pop(0)
            cost = cost_before_strip[-5:]


            #checking to see if title is a random untitled tag with ascii values
            #48 -> 57 are numbers, as theres numbers in certain titles
            #97 -> 122 is a - z
            #if ord(title[0].lower()) < 97 and ord(title[0].lower()) < 48 or ord(title[0].lower()) > 122 and ord(title[0].lower()) > 57:
                #break

            new_game = Game(pct, cost, title)
            
            if new_game not in return_games:
                return_games.append(new_game)

        for i in return_games:
            return_list.append(f'{i.get_title()} - {i.get_cost()} ({i.get_discount()} off)')

        return return_list
    else:
        return "Steam website is down"
    driver.quit()
    
def main ():
    data = top_sellers()
    send_info(data)

#if this application was run directly, run main
if __name__ == "__main__":
    main()