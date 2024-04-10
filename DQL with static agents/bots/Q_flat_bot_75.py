import get_state

class Bot(object):
    """
    Bids 75 on everything
    """
    
    def __init__(self, Qref):
        self.name = "flat_bot_75"
        self.Q_ref = Qref # reference to Q
        
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
        state = get_state.get_state(current_round, bots, painting_order, my_bot_details, current_painting)
        
        action = 0.237
        self.Q_ref.add_state_action_pair(state, action, my_bot_details['bot_unique_id'])
        return get_state.actionToBid(action)