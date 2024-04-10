import random


class Bot(object):
    def __init__(self):
        self.name = (
            "execute_fastest_plan_flexible"  # Put your id number her. String or integer will both work
        )
        self.bid = 0
        # Add your own variables here, if you want to.

    def testForWin(self, painting_count):
        #code stolen from auctioneer.py
        target_collection=[3, 3, 1, 1]
        bot_painting_counts_sorted = sorted(painting_count.values(), reverse=True)

        paintings_needed = [
            target - bot_painting_counts_sorted[index]
            for index, target in enumerate(target_collection)
        ]

        if max(paintings_needed) < 1:
            return True
        return False

    #given you buy everything, returns paintings owned once you win
    def getFastestWinState(self, painting_order, current_count, round_num):
        forwardCount = current_count.copy() #pass by value
        i = 0
        for painting in painting_order:
            if (i < round_num):
                i+=1
                continue

            forwardCount[painting]+=1

            if (self.testForWin(forwardCount)):
                return forwardCount

            i+=1

        return forwardCount
            

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
        currentPaintingsCount = my_bot_details['paintings']
        shouldBuy = {'Da Vinci': False, 'Picasso': False, 'Rembrandt': False, 'Van Gogh': False}
        artists = ['Da Vinci', 'Picasso', 'Rembrandt', 'Van Gogh']

        forwardCount = self.getFastestWinState(painting_order, currentPaintingsCount, current_round)
        for artist in artists:
            
            #buy if dont have it yet
            if (currentPaintingsCount[artist] == 0):
                shouldBuy[artist] = True

            #or if wins the forward count at 3
            if (forwardCount[artist] >= 3 and currentPaintingsCount[artist] < 3):
                shouldBuy[artist] = True

        #buys if should buy to try complete set, 100 as max will ever have is 9 paintings before winning
        if (shouldBuy[current_painting]):
            self.bid = 100
            return 100
        self.bid = 0
        return 0



