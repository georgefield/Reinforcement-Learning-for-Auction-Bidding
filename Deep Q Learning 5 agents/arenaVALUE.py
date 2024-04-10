# Import the auctioneer, to run your auctions
from auctioneer import Auctioneer

# Import some bots to play with
# We have given you some basic bots to start with in the bots folder
# You can also add your own bots to test against

from bots import P_agent
from bots import Q

Qglob = Q.Q(0, 5,"")

def training_rounds(numRounds, standardBots=False):    
    studentBots = [P_agent.Bot(False, 0, Qglob, 1, "", 0.25, 1.5, 0),
                   P_agent.Bot(False, 1, Qglob, 0, "", 0.25, 1.5, 0),
                   P_agent.Bot(False, 2, Qglob, 0, "", 0.25, 1.5, 0),
                   P_agent.Bot(False, 3, Qglob, 0, "", 0.25, 1.5, 0),
                   P_agent.Bot(False, 4, Qglob, 0, "", 0.25, 1.5, 0)]

    # Fits Q and agents every round
    for round in range(numRounds):
        print("-------Round:",round)

        allBroke, bots = run_single_round(studentBots)

        print("\nReturned winner:", bots[0]['bot_name'],",All broke:",allBroke,"\n")

        if (not standardBots):
            for bot in studentBots:
                bot.fit_model(True)

        fitQ = False
        if ((round+1)%2 == 0):
            fitQ = True

        if (not allBroke):
            Qglob.finish_round(bots[0]['bot_unique_id'], fitQ, True)
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