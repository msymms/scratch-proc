from bs4 import BeautifulSoup
import requests as rq
import re
import pandas as pd

# ***GLOBALS***
game_urls = []
numbers = []
g_names = []
g_cost = []
total_tix = []
overall_odds = []
top_prize_odds = []
current_overall_odds = []
current_top_prize_odds = []
overall_odds_delta = []
top_prize_odds_delta =[]
remaining_tix = []  # this is an estimate based on the linear sales of winners * odds

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
# region *********** Process CSV data **************

url = "http://www.txlottery.org/export/sites/lottery/Games/Scratch_Offs/scratchoff.csv"

df = pd.read_csv(url, skiprows=1, encoding='latin1')

df.columns = df.columns.str.strip()

#   Rename the Columns
names = df.columns.tolist()
names[names.index('Game Number')] = 'game_number'
names[names.index('Game Name')] = 'game_name'
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
    df.at[idx, 'prize_level'] = 1040000

if '$500/wk***' in df.values:
    idx = df.prize_level[df.prize_level == '$500/wk***'].index.tolist()
    df.at[idx, 'prize_level'] = 260000

if 'Free Pick 3 Ticket' in df.values:
    idx = df.prize_level[df.prize_level == 'Free Pick 3 Ticket'].index.tolist()
    df.at[idx, 'prize_level'] = 1

if '$777,777' in df.values:
    # strip all non-numeric chars from prize level
    idx = df.prize_level[df.prize_level == '$777,777'].index.tolist()
    df.at[idx, 'prize_level'] = 777777


# Convert prize_level to numeric
df.prize_level = df.prize_level.astype(int)

# replace all NaN with 0
df.prizes_claimed.fillna(0, inplace=True)

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
def remove_games():
    for num in numbers:
        if int(num) in df.game_number.values:
            continue
        else:
            idx = numbers.index(num)
            numbers.remove(num)
            game_urls.pop(idx)
            num=''
            return True


while remove_games():
    pass

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

# region *********** Calculate the Odds and Initial Value Per Ticket ****************

#   add up the total prizes in the game based on game id
for num in numbers:

    try:
        # retreive the subset based on game number
        df2 = df[df.game_number == int(num)]
        # set the game name
        g_names.append(df2.game_name.iloc[0])
        # set the game cost
        g_cost.append(df2.ticket_price.iloc[0])
        # calculate the total amount of winning tickets in game
        tot_prizes = sum(df2.prizes_in_level.values)
        # get the value for the number of top prizes in each game
        num_top_prize = (df2.prizes_in_level.iloc[-1])
        # calculte the total prizes remaining
        tot_rem_prizes = tot_prizes - sum(df2.prizes_claimed)
        # calculate the total top prizes claimed
        top_prize_rem = num_top_prize - df2.prizes_claimed.iloc[-1]

        # # get the total tickets in game based index
        tix = int(total_tix[numbers.index(num)])
        #calculate the initial overall odds
        ov_odds = round(float(tix/tot_prizes),4)
        overall_odds.append(ov_odds)
        #calculate the initial odds for top prize
        top_odds = round(float(tix/num_top_prize), 4)
        top_prize_odds.append(top_odds)
        # calculate the estimated remaining tickets in game
        est_tix_rem = tix - ((sum(df2.prizes_claimed) * (overall_odds[numbers.index(num)] * 1.05)))
        remaining_tix.append(round(est_tix_rem))

        # calculate the current overall odds
        curr_ov_odds = round((est_tix_rem/tot_rem_prizes), 4)
        current_overall_odds.append(curr_ov_odds)
        #calculate the current top prize odds
        curr_top_odds = round((est_tix_rem/top_prize_rem), 4)
        current_top_prize_odds.append(curr_top_odds)

        #calclulate the odds deltas
        overall_odds_delta.append(round((ov_odds - curr_ov_odds), 4))
        top_prize_odds_delta.append(round((top_odds - curr_top_odds), 4))
    except:
        if (df2.empty):
            total_tix.pop(numbers.index(num))
            overall_odds.pop(numbers.index(num))
            continue


# endregion

# region ********** Finish the File *********************

# testing the lengths of the lists
print('Length of numbers ' + str(len(numbers)))
print('Length of g_names ' + str(len(g_names)))
print('Length of total_tix ' + str(len(total_tix)))
print('Length of overall_odds ' + str(len(overall_odds)))
print('Length of remaining_tix ' + str(len(remaining_tix)))
print('Length of overall odds delta ' + str(len(overall_odds_delta)))


# construct the dataframe from the lists
r_df = pd.DataFrame(
    {
        'Game Number': numbers,
        'Name': g_names,
        'Ticket Price': g_cost,
        'Total Tickets': total_tix,
        'Est. Remaining Tickets': remaining_tix,
        'Initial Odds': overall_odds,
        'Current Overall Odds' : current_overall_odds,
        'Overall Delta' : overall_odds_delta,
        'Initial Top Prize Odds': top_prize_odds,
        'Current Top Prize Odds' : current_top_prize_odds,
        'Top Prize Delta' : top_prize_odds_delta
    }
)
# sort the dataframe
results = r_df.sort_values(['Top Prize Delta'], ascending=False)
# write out the CSV

import time

timestr = time.strftime("%m%d%y")
# stream out the file
results.to_csv('~/Desktop/Results' + timestr + '.csv', sep=',')

# endregion
