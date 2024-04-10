import random


class Bot(object):
    def __init__(self):
        self.name = (
            "debug"  # Put your id number her. String or integer will both work
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
        if (current_round <= 3):
            print(
                f"current_round: {current_round}\n",
            )
            print("Bots:")
            for bot in bots:
                print(
                    f"     {bot}"
                )
            print(
                f"\nwinner_pays: {winner_pays}\n",
                f"artists_and_values: {artists_and_values}\n",
                f"round_limit: {round_limit}\n",
                f"starting_budget: {starting_budget}\n",
                f"painting_order: {painting_order}\n",
                f"target_collection: {target_collection}\n",
                f"my_bot_details: {my_bot_details}\n",
                f"current_painting: {current_painting}\n",
                f"winner_ids: {winner_ids}\n",
                f"amounts_paid: {amounts_paid}\n"
            )
        return 0