# Import the auctioneer, to run your auctions
from auctioneer import Auctioneer

# Import some bots to play with
# We have given you some basic bots to start with in the bots folder
# You can also add your own bots to test against

from bots import debug_bot
from bots import u2013389

from bots import greedy_botp1
from bots import greedy_botp1_copy
from bots import execute_fastest_plan_inflexiblep1

from bots import budget_third
from bots import greedy_bot
from bots import execute_fastest_plan_flexible
from bots import execute_fastest_plan_inflexible
from bots import flat_bot_10
from bots import flat_bot_50
from bots import flat_bot_75
from bots import flat_bot_100
from bots import flat_bot_125
from bots import flat_bot_175
from bots import random_bot

from bots import play_small_model
from bots import play_large_model

from bots import play_small_model225
from bots import play_small_model150
from bots import play_small_model175
from bots import play_small_model200

import random

#standardBots = [play_small_model,
                #budget_third, 
                #greedy_bot, 
                #execute_fastest_plan_flexible, 
                #execute_fastest_plan_inflexible, 
                #flat_bot_50, 
                #flat_bot_75,
                #flat_bot_100, 
                #flat_bot_125,
                #random_bot]

standardBots= [play_small_model, play_small_model225, play_small_model150, play_small_model175, play_small_model200]

def run_lots_of_auctions():
    """
    An example if you want to run alot of auctions at once
    """
    # A large room with a few bots of the same type
    #room = [play_large_model, play_small_model]
    room = [play_small_model, execute_fastest_plan_inflexiblep1, greedy_botp1]

    winnersTotal = {}
    for bot in room:
        winnersTotal[bot.Bot().name] = 0

    run_count = 100 #Standard gauntlet execution
    for i in range(run_count):
        print("---------- Round",i+1)
        for bot_module in room:
            print("    ",bot_module.Bot().name)

        my_auction = Auctioneer(room=room, slowdown=0, verbose=False)
        # run_auction() returns a list of winners, sometimes there are more than one winner if there is a tie
        winners = my_auction.run_auction()
        print("Round ", i+1, " winner:", winners)
        for winner in winners:
            winnersTotal[winner] += 1

    print("---------RESULTS---------")
    print(winnersTotal)


if __name__ == "__main__":
    run_lots_of_auctions()
