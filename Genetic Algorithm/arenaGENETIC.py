# Import the auctioneer, to run your auctions
from auctioneer import Auctioneer

# Import some bots to play with
# We have given you some basic bots to start with in the bots folder
# You can also add your own bots to test against
from bots import network_training_GA

import random
import numpy as np


def do_GA_rounds(GArounds, roundsPerCull, bots, numSurvivingBots, startRound):
    surviving_bots = numSurvivingBots
    num_bots = len(bots)
    for round in range(GArounds):
        
        print("\n\nRound start --------------",round)
        print("Bots:")
        for i in range(num_bots):
            print("  bot id:",bots[i].randomID)

        sorted_scores, sorted_bots = score_single_GA_round(roundsPerCull, bots) # returned sorted best to worst

        print("\n\nRound done  --------------",round)
        print("Bots, best",surviving_bots," repopulate and are saved:")

        # save surving every round
        for i in range(num_bots):
            for bot in bots:
                if (bot.randomID == sorted_bots[i].randomID):
                    print("bot instance:", sorted_bots[i].name, "bot id:", sorted_bots[i].randomID, "score:", sorted_scores[i])
                    if (i == 0): # save best
                        bots[i].model.save("best_SGAbot" + str(round + startRound) + ".keras")

                    if (i < surviving_bots): # save GA state
                        bots[i].model.save("SGAbot" + str(i) + ".keras")
                    else: # cull bad bots
                        parents = np.random.choice(np.arange(surviving_bots), 2, replace=False)
                        bot.replaceModelWithChild(sorted_bots[parents[0]].model, sorted_bots[parents[1]].model, 0.01, 0.05)

    return bots

def score_single_GA_round(roundsPerCull, bots):

    bot_scores = []
    bots_played = []
    for i in range(len(bots)):
        bot_scores.append(0)
        bots_played.append(0)

    below = 1
    for i in range(roundsPerCull):
        print("\n  Sub round:", i,"-----------")
        n = 2
        #for n in range(2,len(bots)):
            #if (n > 2):
                #continue
        
        bots_to_play_nums = []

        np_bots_played = np.array([bots_played])
        select_from = np.where(np_bots_played < below)[1]
        print(select_from, below)
        if  len(select_from) < n:
            below+=1
            select_from = np.where(np_bots_played < below)[1]
        
        bots_to_play_nums = np.random.choice(select_from, n, replace=False)

        new_room = []
        for i in bots_to_play_nums:
            new_room.append(bots[i])
            bots_played[i] += 1

        my_auction = Auctioneer(room=new_room, slowdown=0, verbose=False)
        all_budgets_0, bots_output = my_auction.run_auction()
        count = 0

        for i in bots_to_play_nums:
            score = bots[i].scoreState(bots_output[count], all_budgets_0)
            print("bot ", bots[i].name, " scored ", score)
            bot_scores[i] += score
            count+=1

    print("bots played:",bots_played)
    for i in range(len(bot_scores)):
        if (bots_played[i] != 0):
            bot_scores[i] /= bots_played[i] # return bots average score per round
    combined_scores_and_bots = list(zip(bot_scores, bots))

    # Sort the combined list based on the first list
    sorted_combined = (sorted(combined_scores_and_bots, key=lambda x: x[0]))[::-1]
    sorted_list_scores, sorted_list_room = zip(*sorted_combined)
    return sorted_list_scores, sorted_list_room


if __name__ == "__main__":

    fromScratch = True
    bots = []
    num_bots = 50
    surviving_bots = 25

    if (fromScratch):
        for i in range(num_bots):
            bots.append(network_training_GA.Bot(i, "RegressionBotSmall.keras"))
            if (i > surviving_bots):
                bots[i].replaceModel(bots[0].model, 0.01, 0.05) # Start with small mutations on all but 1
    else:
        for i in range(num_bots):
            if (i < surviving_bots):
                bots.append(network_training_GA.Bot(i, "SGAbot" + str(i) + ".keras"))
            else:
                bots.append(network_training_GA.Bot(i))
                parents = np.random.choice(np.arange(surviving_bots), 2, replace=False)
                bots[-1].replaceModelWithChild(bots[parents[0]].model, bots[parents[1]].model, 0.05, 0.15) # Mutation rate, mutation standard dev

    do_GA_rounds(100, 100, bots, surviving_bots, 4)