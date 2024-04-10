import random
import get_state

class Bot(object):
    def __init__(self, Qref):
        self.name = (
            "greedy_bot"
        )
        self.Q_ref = Qref

    # Don't deep copy Q!!!
    def __deepcopy__(self, memo):
        # Create a new instance of the Bot class
        new_bot = Bot(self.Q_ref)  # Assuming 'name' is the only required attribute for initialization
        return new_bot


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
    
        state = get_state.get_state(current_round, bots, painting_order, my_bot_details, current_painting)

        #buys if should buy to try complete set
        if (shouldBuy[current_painting]):
            action = 0.5
            self.Q_ref.add_state_action_pair(state, action, my_bot_details['bot_unique_id'])
            return get_state.actionToBid(action)
        
        action = 0
        self.Q_ref.add_state_action_pair(state, action, my_bot_details['bot_unique_id'])
        return get_state.actionToBid(action)



