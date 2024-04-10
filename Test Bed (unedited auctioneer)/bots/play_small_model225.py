from keras.models import load_model
import numpy as np

import random
import get_state

class Bot(object):
    def __init__(self, load=True):
        self.name = (
            "my_bot225"  # Put your id number her. String or integer will both work
        )
        if (load):
            self.model = load_model('Bot0epoch225.keras')
        
    # dont deep copy model
    def __deepcopy__(self, memo):
        # Create a new instance of the Bot class
        new_bot = Bot(False)
        
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
        state = get_state.get_state(current_round, bots, painting_order, my_bot_details, current_painting)
        action = self.model.predict(get_state.get_state_as_model_input(state), verbose=0)[0][0]

        bid = min(get_state.actionToBid(action), my_bot_details['budget'])
        print(self.name, "bid", bid)
        return bid
