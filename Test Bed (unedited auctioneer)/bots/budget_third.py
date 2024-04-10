import random


class Bot(object):
    def __init__(self):
        self.name = (
            "budget third"
        )
        self.bid = 0

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
        self.bid = my_budget/3
        return self.bid
