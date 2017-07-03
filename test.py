from bs4 import BeautifulSoup
import requests as rq
import string
import re
import pandas as pd
from games import Games

# ***GLOBALS***
numbers = []
game_urls = []
total_tix = []


# grab the data from the lottery website
# we need to grab the csv file and load it into the dataframe
# then we grab the urls for each game
# from then we grab the total tickets
# once we have the total tickets we can calculate the initial value per ticket.
# Then we want to calculate the tickets left and the money left in each game
# From there we can determine the current value per ticket.

# region ***********  Process CSV data **************
# url = "http://www.txlottery.org/export/sites/lottery/Games/Scratch_Offs/scratchoff.csv"
#
# df = pd.read_csv(url, skiprows=1, encoding='latin1')
#
# df.columns = df.columns.str.strip()
#
# #   Rename the Columns
# names = df.columns.tolist()
# names[names.index('Game Number')] = 'game_number'
# names[names.index('Game Name')] = 'game_name'
# names[names.index('Game Close Date')] = 'close_date'
# names[names.index('Ticket Price')] = 'ticket_price'
# names[names.index('Prize Level')] = 'prize_level'
# names[names.index('Total Prizes in Level')] = 'prizes_in_level'
# names[names.index('Prizes Claimed')] = 'prizes_claimed'
# df.columns = names
#
# # Remove the 'Total' Rows
# df = df[df.prize_level != 'TOTAL']

#  WE NEED TO PROCESS THE DATA AND UPDATE THE RESULTS DATA
# endregion

# region **************** Retrieve the Links to each Game *****************
url = "http://www.txlottery.org/export/sites/lottery/Games/Scratch_Offs/all.html_1980914485.html"

response = rq.get(url)

soup = BeautifulSoup(response.content, "html.parser")

tablebody = soup.tbody

links = tablebody.find_all('a')

for tag in links:
    numbers.append(tag.string)
    game_urls.append(tag['href'])

# endregion

# region ******************Grab the total number of tickets and load into a list *****************

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

print(total_tix)

# endregion
