# Import the auctioneer, to run your auctions
from auctioneer import Auctioneer

# Import some bots to play with
# We have given you some basic bots to start with in the bots folder
# You can also add your own bots to test against
from bots import network_training
from bots import network_training_smaller


from bots import budget_third
from bots import execute_fastest_plan_flexible
from bots import execute_fastest_plan_inflexible
from bots import flat_bot_10
from bots import flat_bot_50
from bots import flat_bot_125
from bots import greedy_bot
from bots import random_bot

standardBots = [budget_third, execute_fastest_plan_flexible, execute_fastest_plan_inflexible, flat_bot_10, flat_bot_50, flat_bot_125, greedy_bot, random_bot]

import random

def training_rounds(studentBot, numRounds):    
    for round in range(numRounds + 1):
        print("round:",round)
        room = [studentBot]

        numOtherBots = random.randint(-4,9)
        numOtherBots = max(1,numOtherBots) #more time is 1 other bot
        for i in range(numOtherBots):
            room.append(standardBots[random.randint(0,len(standardBots)-1)].Bot()) #bots name is i index

        run_single_round(room)
        if (round % 10 == 0):
            studentBot.fit_model()

def run_single_round(room):
    # Setup the auction
    my_auction = Auctioneer(room=room, slowdown=0, verbose=False)
    # run_auction() returns a list of winners, sometimes there are more than one winner if there is a tie
    my_auction.run_auction()



if __name__ == "__main__":
    print("GO")
    #studentBot = network_training.Bot(0)
    studentBot = network_training_smaller.Bot(0)

    training_rounds(studentBot, 1000)