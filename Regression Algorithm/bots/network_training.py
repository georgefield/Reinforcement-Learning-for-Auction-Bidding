import random

from keras import Sequential
from keras.layers import Dense
from keras.models import load_model
from keras import regularizers

import numpy as np

class Bot(object):
    def __init__(self, bot_id, loadModel="",copy=False):
        self.name = (
            str(bot_id)  # Put your id number her. String or integer will both work
        )
        if (copy):
            return
        
        self.randomID = random.randint(1,100)
        self.paintingLookahead = 10

        if (loadModel == ""):
            self.model = Sequential()
            self.model.add(Dense(units=64, activation='relu', input_dim=(180+(4*self.paintingLookahead)), kernel_regularizer=regularizers.L2(1e-4)))
            self.model.add(Dense(units=10, activation='relu', kernel_regularizer=regularizers.L2(1e-4)))
            self.model.add(Dense(units=1, activation='sigmoid', kernel_regularizer=regularizers.L2(1e-4)))
            self.model.compile(optimizer='adam', loss='mse', metrics=['mae'])  # Use mean squared error for loss
        else:
            self.model = load_model('studentbot.keras')

        self.batchX = [] # array of 'combinedNParr', the input info
        self.batchY = [] # array of 'greedyBotBidNORM', the target
        self.batchPredictions = []

        self.myInfo = []

        self.epoch = 0

    def __deepcopy__(self, memo):
        # Create a new instance of the Bot class
        new_bot = Bot(self.name, "", True)  # Assuming 'name' is the only required attribute for initialization
        
        return new_bot
        
    def get_name(self):
        return self.name

    def get_greedybot_bid(
            self,
            my_bot_details,
            current_painting
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

        #*** TARGET FOR NETWORK ***
        greedyBotBid = self.get_greedybot_bid(my_bot_details, current_painting)
        target = (greedyBotBid/1001.0) # train to undershoot so beginning network doesnt run out of budget

        #*** STORE INFO ***
        self.batchX.append(modelInput)
        self.batchY.append(target) 

        return greedyBotBid

    def fit_model(self, showEval = True):
        # Convert batch lists to numpy arrays
        batchX_np = np.vstack(self.batchX)
        batchY_np = np.array(self.batchY)

        # Print error (should get smaller every round)
        predictions = self.model.predict(batchX_np)
        mse = np.mean((np.array(predictions) - batchY_np) ** 2)
        if (showEval):
            print("Epoch:", self.epoch, "Mean squared error:", mse)
        
        self.saveModel(mse)

        self.epoch+=1

        # Clear batch lists ready for next
        self.batchX = []
        self.batchY = []
        # Fit the model with the batch data
        self.model.fit(batchX_np, batchY_np, epochs=self.epoch, batch_size=len(batchY_np), verbose=0)  # Adjust parameters as needed        

    def saveModel(self, mse):
        with open("Regression"+str(self.name)+"_mse_log.txt", "a") as file:
            file.write(f"epoch {self.epoch}: {mse}\n")
        self.model.save('RegressionBot.keras')