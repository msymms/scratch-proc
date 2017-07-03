import sys
# sys.path.append('/Library/Python/2.7/site-packages')
from bs4 import BeautifulSoup
import urllib3 as ul
import pandas as pd
from games import Games

# grab the data from the lottery website
# we need to grab the csv file and load it into th etable
# then we grab the urls for each game
# from then we grab the game name and total tickets


# ***********  Process CSV data **************
# grab the csv for current game data
url = "http://www.txlottery.org/export/sites/lottery/Games/Scratch_Offs/scratchoff.csv"

http = ul.PoolManager()

df = pd.read_csv(url, skiprows=1, encoding='latin1')

df.columns = df.columns.str.strip()

#   Rename the Columns
names = df.columns.tolist()
names[names.index('Game Number')] = 'game_number'
names[names.index('Game Name')] = 'game_name'
names[names.index('Game Close Date')] = 'close_date'
names[names.index('Ticket Price')] = 'ticket_price'
names[names.index('Prize Level')] = 'prize_level'
names[names.index('Total Prizes in Level')] = 'prizes_in_level'
names[names.index('Prizes Claimed')] = 'prizes_claimed'
df.columns = names

# Remove the 'Total' Rows
df = df[df.prize_level != 'TOTAL']

#  WE NEED TO PROCESS THE DATA AND UPDATE THE RESULTS DATA


url = "http://www.txlottery.org/export/sites/lottery/Games/Scratch_Offs/all.html_1980914485.html"

response = http.request('GET', url)

soup = BeautifulSoup(response, "html.parser")

# file = open("testfile.txt", "w")
# file.write(soup.prettify())
# file.close()
# tablebody = soup.tbody

# links = tablebody.find_all('a')
# print(len(links))
