from keras.models import load_model
import numpy as np

class Bot(object):
    def __init__(self, load=True):
        self.name = (
            "RegressionBot"  # Put your id number her. String or integer will both work
        )
        if (load):
            self.model = load_model('greedyp5model_large.keras')
        self.paintingLookahead = 10

        self.myInfo = []
        
    # dont deep copy model
    def __deepcopy__(self, memo):
        # Create a new instance of the Bot class
        new_bot = Bot(False)
        
        return new_bot

    def get_paintings_binary_encoding(self, paintings):
        encoding = []
        for numOfArtist in paintings.values():
            tmp = [0,0,0,0]
            tmp[min(3, numOfArtist)] = 1
            encoding.extend(tmp)
        return encoding

    def get_artist_binary_encoding(self, artist):
        artistDict = {
            "Da Vinci": 0,
            "Rembrandt": 1,
            "Van Gogh": 2,
            "Picasso": 3,
        }
        encoding = [0,0,0,0]
        encoding[artistDict[artist]] = 1
        return encoding


    def updateMyInfo(self,my_bot_details):
        self.myInfo = [1] # formatted: budget, paintings encoded
        self.myInfo.append(my_bot_details['budget'] / 1001.0)
        self.myInfo.extend(self.get_paintings_binary_encoding(my_bot_details['paintings']))


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
        #****** PREPROCESS DATA FOR MORE COHERENT NETWORK INPUT ******

        #*** MY BOT DETAILS ***
        self.updateMyInfo(my_bot_details)

        #*** OTHER BOT DETAILS ***
        otherBotInfo = [] # formatted: playing, norm budget, paintings encoded - playing, norm budget, paintings encoded - ... for the 9 other spaces in the room  
        for i in range(10):
            if (i < len(bots)):
                bot = bots[i]
                if (bot['bot_name'] == self.name): # dont add self info again
                    continue
                otherBotInfo.append(1)
                otherBotInfo.append(bot['budget'] / 1001.0)
                otherBotInfo.extend(self.get_paintings_binary_encoding(bot['paintings']))
            else:
                otherBotInfo.append(0)
                otherBotInfo.append(0)
                otherBotInfo.extend([0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0])


        #*** AUCTION DETAILS ***
        paintingsOrderBinaryEncoding = [] # includes current painting and next [paintingLookahead] paintings
        for i in range(self.paintingLookahead): # next 10 artists
            if (current_round + i >= len(painting_order)):
                paintingsOrderBinaryEncoding.extend([0,0,0,0])
                continue
            paintingsOrderBinaryEncoding.extend(self.get_artist_binary_encoding(painting_order[current_round + i]))

        #*** COMBINE ALL INTO INPUT ARRAY ***

        #*** RESHAPE FOR INPUT TO MODEL ***
        combined = np.concatenate([self.myInfo, otherBotInfo, paintingsOrderBinaryEncoding])
        modelInput = combined.reshape((1, len(combined)))

        bidFrac = self.model.predict(modelInput, verbose=0)

        bid = bidFrac * 1001
        print("large model:", min(bid, my_bot_details['budget']))
        return min(bid, my_bot_details['budget'])     
