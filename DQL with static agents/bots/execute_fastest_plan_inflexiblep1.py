import random


class Bot(object):
    def __init__(self):
        self.name = (
            "execute_fastest_plan_inflexiblep1"  # Put your id number her. String or integer will both work
        )
        self.usedp1 = False
        # Add your own variables here, if you want to.

    def get_painting_rarity(self,painting, next_painting_order):
        howFarLook = min(len(next_painting_order), 25)
        count = next_painting_order[:howFarLook].count(painting)
        return count/25
    
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

    def geqCount(self, current_count, geqThan):
        count = 0
        for painting in current_count:
            if (current_count[painting] >= geqThan):
                count += 1
        return count

    #given you buy everything, returns paintings owned once you win
    def getFastestWinState(self, painting_order, current_count, round_num):
        forwardCount = current_count.copy() #pass by value

        i = 0
        for painting in painting_order:
            if (i < round_num):
                i+=1
                continue

            forwardCount[painting]+=1
            if (self.geqCount(forwardCount, 3) > 2):
                forwardCount[painting]-=1

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
            if (not self.usedp1 and self.get_painting_rarity(current_painting, painting_order) < 0.25):
                self.usedp1 = True
                return 126
            return 125
        return 0



