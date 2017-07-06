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
g_cost = []
total_tix = []
tot_money_in_game = []
game_probability = []
remaining_tix = []      #this is an estimate based on the linear sales of winners * probability
cur_money_in_game = []
# init_value_per_ticket = []
# cur_value_per_ticket = []
# change_in_value = []
percent_money = []
percent_tix = []



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

#replace all NaN with 0
df.prizes_claimed.fillna(0, inplace = True)


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

# remove games that are not in the csv file - these are usually games that have not started.
for num in numbers:
    if int(num) in df.game_number.values:
        continue
    else:
        idx = numbers.index(num)
        numbers.remove(num)
        game_urls.pop(idx)

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
    game_probability.append(temp2)


# endregion

# region *********** Calculate the Odds and Initial Value Per Ticket ****************

i = 0

#   add up the total prizes in the game based on game id
for num in numbers:
    # retreive the subset based on game number
    df2 = df[df.game_number == int(num)]
    # set the game name
    g_names.append(df2.game_name.iloc[0])
    # set the game cost
    g_cost.append(df2.ticket_price.iloc[0])
    # calculate the total amount of winning tickets in game
    tot_prizes = sum(df2.prizes_in_level.values)
    # calculate the amount of money at each prize level
    tot_money_at_level = df2.prize_level * df2.prizes_in_level
    # calculate the initial amount of money in the game
    tot_money_in_game.append(sum(tot_money_at_level))
    # calculate current money in game
    cur_money_at_level = (df2.prizes_in_level - df2.prizes_claimed) * df2.prize_level
    # calculate the current amount of money in the game
    cur_money_in_game.append(sum(cur_money_at_level.values))
    # get the total tickets in game based index
    tix = int(total_tix[i])
    prob = float(game_probability[i])
    # calculate the estimated remaining tickets in game
    est_tix_rem = tix - (sum(df2.prizes_claimed) * 2.5)
    remaining_tix.append(est_tix_rem)
    # # calculate the initial value per ticket
    # init_tix_val = format((sum(tot_money_at_level) / tix), '.2f')
    # # add to list
    # init_value_per_ticket.append(init_tix_val)
    # #calculate the current value per ticket
    # cur_tix_val = format(((sum(cur_money_at_level)) / est_tix_rem), '.2f')
    # # add to list
    # cur_value_per_ticket.append(cur_tix_val)
    # # calculate the change in value
    # ch_val = float(cur_tix_val) - float(init_tix_val)
    # change_in_value.append(ch_val)
    # calculate the percentage of tickets left
    pct_prizes = 1 - (sum(df2.prizes_claimed) / tot_prizes)
    percent_tix.append(pct_prizes)
    # calculate the percetage of money left
    pct_money = sum(cur_money_at_level.values) / sum(tot_money_at_level)
    percent_money.append(pct_money)

    #increment the indexer
    i = i + 1

# endregion

# region ********** Finish the File *********************

# testing teh lengths of the lists
# print('Length of numbers ' + str(len(numbers)))
# print('Length of g_names ' + str(len(g_names)))
# print('Length of total_tix ' + str(len(total_tix)))
# print('Length of tot_money_in_game ' + str(len(tot_money_in_game)))
# print('Length of game_probability ' + str(len(game_probability)))
# print('Length of remaining_tix ' + str(len(remaining_tix)))
# print('Length of cur_money_in_game ' + str(len(cur_money_in_game)))
# print('Length of init_value_per_ticket ' + str(len(init_value_per_ticket)))
# print('Length of cur_value_per_ticket ' + str(len(cur_value_per_ticket)))
# print('Length of change_in_value ' + str(len(change_in_value)))



    # construct the dataframe from the lists
r_df = pd.DataFrame(
    {
        'Game Number': numbers,
        'Name': g_names,
        'Ticket Price': g_cost,
        'Total Tickets': total_tix,
        'Total Money in Game': tot_money_in_game,
        'Probability': game_probability,
        'Remaining Tickets': remaining_tix,
        'Current Money in Game': cur_money_in_game,
        '% Prizes Left': percent_tix,
        '% Money Left': percent_money,
    }
)
    # sort the dataframe
results = r_df.sort_values(['% Money Left'], ascending=False)
    # write out the CSV

import time
timestr = time.strftime("%m%d%y")
# results.to_csv('C:/Users/Mark/Desktop/Results.csv', sep=',')

results.to_csv('~/Desktop/Results' + timestr + '.csv', sep=',')


# endregion
