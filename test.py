from bs4 import BeautifulSoup
import requests as rq
import string
import re
import pandas as pd
from games import Games

# ***GLOBALS***
game_urls = []
numbers = []
g_names = []
total_tix = []
tot_money_in_game = []
game_probability = []
remaining_tix = []      #this is an estimate based on the linear sales of winners * probability
cur_money_in_game = []
init_value_per_ticket = []
cur_value_per_ticket = []
change_in_value = []



# grab the data from the lottery website
# we need to grab the csv file and load it into the dataframe
# then we grab the urls for each game
# from then we grab the total tickets
# once we have the total tickets we can calculate the initial value per ticket.
# Then we want to calculate the tickets left and the money left in each game
# From there we can determine the current value per ticket.

# region *********** Process CSV data **************

url = "http://www.txlottery.org/export/sites/lottery/Games/Scratch_Offs/scratchoff.csv"

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

# fix prize levels for weekly awards
if '$1,000/wk***' in df.values:
    idx = df.prize_level[df.prize_level == '$1,000/wk***'].index.tolist()
    df.set_value(idx,'prize_level', 1040000)

if '$2,500/wk***' in df.values:
    idx = df.prize_level[df.prize_level == '$2,500/wk***'].index.tolist()
    df.set_value(idx, 'prize_level', 2600000)

# Convert prize_level to numeric
df.prize_level = df.prize_level.astype(int)

# endregion

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


# endregion

# region *********** Cacluate the Odds and Initial Value Per Ticket ****************

i = 0

#   add up the total prizes in the game based on game id
for num in numbers:
    # retreive the subset based on game number
    df2 = df[df.game_number == int(num)]
    # set the game name
    g_names.append(df2.game_name)
    # calculate the total amount of winning tickets in game
    tot_prizes = sum(df2.prizes_in_level)
    # calculate the amount of money at each prize level
    tot_money_at_level = df2.prize_level * df2.prizes_in_level
    # calculate the initial amount of money in the game
    tot_money_in_game.append(sum(tot_money_at_level))
    # calculate current money in game
    cur_money_at_level = (df2.prizes_in_level - df2.prizes_claimed) * df2.prize_level
    # calculate the current amount of money in the game
    cur_money_in_game.append(sum(cur_money_at_level))
    # get the total tickets in game based index
    tix = int(total_tix[i])
    # calculate the probability of the game
    prob = tot_prizes / tix
    # calculate the estimated remaining tickets in game
    est_tix_rem = tix - (sum(df.prizes_claimed) * prob)
    # calculate the initial value per ticket
    init_tix_val = tix / sum(tot_money_at_level)
    # add to list
    init_value_per_ticket.append(init_tix_val)
    #calculate the current value per ticket
    cur_tix_val = est_tix_rem / (sum(cur_money_at_level))
    # add to list
    cur_value_per_ticket.append(cur_tix_val)
    # calculate the change in value
    ch_val = cur_tix_val - init_tix_val

    #increment the indexer
    i += i

# endregion

# region ********** Finish the File *********************
    # remove duplicates from g_names
g_names = list(set(g_names))
    # construct the dataframe from the lists
r_df = pd.DataFrame(
    {
        'game_number': numbers,
        'game_name': g_names,
        'total_tickets': total_tix,
        'tot_money_in_game': tot_money_in_game,
        'game_probability': game_probability,
        'remaining_tix': remaining_tix,
        'cur_money_in_game': cur_money_in_game,
        'init_value_per_ticket': init_value_per_ticket,
        'cur_value_per_ticket': cur_value_per_ticket,
        'change_in_value': change_in_value
    }
)

    # sort the dataframe
results = r_df.sort_values(['change_in_value'], ascending=False)
    # write out the CSV
results.to_csv('~/Desktop/Results.csv', sep = ',')


# endregion
