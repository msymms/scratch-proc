from bs4 import BeautifulSoup
import requests as rq
import re
import pandas as pd

#************** Pseudo Code ******************
#   The premise is this:  Each game has an initial overall odds and top_prize odds.
#   As the game progresses those odds change becuase tix are sold and prizes are claimed.
#   The program seeks to identify those games whose odds have changed in favor of the player.
#
#   1. Grab the CSV from the lottery website
#   2. Load into a data frame
#   3. Go to all page and scrape all the game urls
#   4. scrape from each game the Total Tix;
#   5. Determine initial
#       Overall Odds
#       Top Prize Odds
#   6. Calculate the remaining tickets as a factor of overall odds
#   7. Determine (at time T)
#       Overall Odds
#       Top Prize Odds
#       Overall delta
#       Top Prize delta
#
#*********************************************

# ***********  Process CSV data **************
numbers = []
game_numbers = []
game_urls = []
total_tix = []
prob = []

# region *********** Retrieve the Links to each Game *****************

url = "http://www.txlottery.org/export/sites/lottery/Games/Scratch_Offs/all.html"

response = rq.get(url)

soup = BeautifulSoup(response.content, "html.parser")

tablebody = soup.tbody

links = tablebody.find_all('a')

for tag in links:
    numbers.append(tag.string)
    game_urls.append(tag['href'])

# endregion

# region *********** Grab the total number of tickets and load into a list *****************

for link in game_urls:
    url = 'http://www.txlottery.org' + link
    response = rq.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    temp_str = soup.find('p', class_='scratchoffDetailsApproxTickets').string
    temp_str = str(temp_str).replace(',', '')
    temp_str = temp_str.rsplit('*')[0]
    temp_str = re.findall('\d+', temp_str)
    temp2 = int(str(temp_str[0]))
    total_tix.append(temp2)

    temp_str = soup.find('p', class_='scratchoffDetailsOdds').string
    temp_str = temp_str.rsplit('*')[0]
    temp2 = float(str(temp_str[-4:]))
    prob.append(temp2)

    # endregion
