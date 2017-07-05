from bs4 import BeautifulSoup
import requests as rq
import re
import pandas as pd

# grab the data from the lottery website
# we need to grab the csv file and load it into the dataframe
# then we grab the urls for each game
# from then we grab the total tickets
# once we have the total tickets we can calculate the initial value per ticket.
# Then we want to calculate the tickets left and the money left in each game
# From there we can determine the current value per ticket.

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
