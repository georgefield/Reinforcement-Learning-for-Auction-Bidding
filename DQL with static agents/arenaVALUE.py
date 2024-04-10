# Import the auctioneer, to run your auctions
from auctioneer import Auctioneer

# Import some bots to play with
# We have given you some basic bots to start with in the bots folder
# You can also add your own bots to test against
from bots import P_agent


from bots import Q_prop_of_budget
from bots import Q_execute_fastest_plan_flexible
from bots import Q_execute_fastest_plan_inflexible
from bots import Q_flat_bot_10
from bots import Q_flat_bot_50
from bots import Q_flat_bot_75
from bots import Q_flat_bot_100
from bots import Q_flat_bot_125
from bots import Q_flat_bot_175
from bots import Q_greedy_bot
from bots import Q_random_bot
from bots import Q_play_small_model
from bots import greedy_botp1
from bots import execute_fastest_plan_inflexiblep1

standardBots = [Q_prop_of_budget, Q_execute_fastest_plan_flexible, Q_execute_fastest_plan_inflexible, Q_flat_bot_10, Q_flat_bot_50, Q_flat_bot_125, Q_greedy_bot, Q_random_bot]

import random

from bots import Q

Qglob = Q.Q(75, 5, "Qepoch75DMstart.keras")

def training_rounds(numRounds, standardBots=False):    
    studentBots = [P_agent.Bot(False, 0, Qglob, 1, "Bot0epoch175.keras", 0.5, 1.5, 175, 5),
                   P_agent.Bot(False, 1, Qglob, 0, "Bot1epoch175.keras", 0.5, 1.5, 175, 5),
                   Q_play_small_model.Bot(Qglob, True, "Bot0epoch150.keras"),
                   Q_play_small_model.Bot(Qglob, True, "Bot0epoch175.keras"),
                   Q_greedy_bot.Bot(Qglob)]


    # Fits Q and agents every round
    for round in range(numRounds):
        print("-------Round:",round + 1)

        allBroke, bots = run_single_round(studentBots)

        print("\nReturned winner:", bots[0]['bot_unique_id'], ",All broke:",allBroke,"\n")

        if (not standardBots):
            for bot in studentBots:
                # Fit all agents with models to approximate max action from Q[s,a]
                fit_model = getattr(bot, "fit_model", None)
                if (callable(fit_model)):
                    fit_model(True)

        fitQ = False
        # 2 Rounds per fitting of Q
        if ((round+1)%2 == 0):
            fitQ = True

        winnerId = bots[0]['bot_unique_id']
        if (not allBroke):
            Qglob.finish_round(winnerId, fitQ, True)
        else:
            # No winner if all ran out of money
            Qglob.finish_round('-', fitQ, True)


def run_single_round(room):
    # Setup the auction
    my_auction = Auctioneer(room=room, slowdown=0, verbose=False)
    # run_auction() returns a list of winners, sometimes there are more than one winner if there is a tie
    return my_auction.run_auction()



if __name__ == "__main__":

    training_rounds(1000)