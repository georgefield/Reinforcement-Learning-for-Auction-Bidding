import random


class Bot(object):
    def __init__(self):
        self.name = (
            "2013389"  # Put your id number her. String or integer will both work
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
        my_budget = my_bot_details["budget"]
        return my_budget/2
