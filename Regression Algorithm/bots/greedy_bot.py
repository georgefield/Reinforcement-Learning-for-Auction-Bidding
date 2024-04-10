import random


class Bot(object):
    def __init__(self):
        self.name = (
            "greedy_bot"  # Put your id number her. String or integer will both work
        )
        # Add your own variables here, if you want to.

    def get_bid(
        self,
        current_round,
        bots,
        winner_pays,
        artists_and_values,
        round_limit,
        starting_budget,
        painting_order,
        target_collection,
        my_bot_details,
        current_painting,
        winner_ids,
        amounts_paid,
    ):
        paintingsIhave = my_bot_details['paintings']
        shouldBuy = {'Da Vinci': False, 'Picasso': False, 'Rembrandt': False, 'Van Gogh': False}

        #get 2 count
        geqTwoCount = 0
        for artist in paintingsIhave:
            if (paintingsIhave[artist] >= 2):
                geqTwoCount += 1

        #set to true for artist I should buy to get collection
        for artist in paintingsIhave:
            if (paintingsIhave[artist] == 2):
                shouldBuy[artist] = True
            elif (paintingsIhave[artist] == 1 and geqTwoCount < 2):
                shouldBuy[artist] = True
            elif (paintingsIhave[artist] == 0):
                shouldBuy[artist] = True
    
        #buys if should buy to try complete set
        if (shouldBuy[current_painting]):
            return 125
        return 0



