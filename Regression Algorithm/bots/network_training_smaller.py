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

        self.paintingLookahead = 5
        self.numInputCompetitors = 2

        if (loadModel == ""):
            self.model = Sequential()
            inputDim = 4+(4*self.numInputCompetitors)+(3*self.paintingLookahead)
            self.model.add(Dense(units=20, activation='relu', input_dim=inputDim, kernel_regularizer=regularizers.L2(1e-4)))
            self.model.add(Dense(units=10, activation='relu', kernel_regularizer=regularizers.L2(1e-4)))
            self.model.add(Dense(units=1, activation='sigmoid', kernel_regularizer=regularizers.L2(1e-4)))
            self.model.compile(optimizer='adam', loss='mse', metrics=['mae'])  # Use mean squared error for loss
        else:
            self.model = load_model('studentbot.keras')

        self.batchX = [] # array of 'combinedNParr', the input info
        self.batchY = [] # array of 'greedyBotBidNORM', the target
        self.batchPredictions = []

        self.epoch = 0

    def __deepcopy__(self, memo):
        # Create a new instance of the Bot class
        new_bot = Bot(self.name, "", True)  # Assuming 'name' is the only required attribute for initialization
        
        return new_bot

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
    
    def distanceToTargetDistributionMeasure(self, paintings):
        artistValues= paintings.values()
        sortedArtistValues = sorted(artistValues)[::-1]
        difference = max(3 - sortedArtistValues[0], 0)
        difference += max(3 - sortedArtistValues[1], 0)
        difference += max(1 - sortedArtistValues[2], 0)
        difference += max(1 - sortedArtistValues[3], 0)
        return difference
    
    def get_need_want_pair(self, current_painting, paintings_i_have):
        if (paintings_i_have[current_painting] == 0 or paintings_i_have[current_painting] == 2):
            return [1,0]
        if (paintings_i_have[current_painting] == 1):
            return [0,1]
        return [0,0]

    def get_painting_rarity(self, painting, next_painting_order):
        howFarLook = min(len(next_painting_order), 20)
        count = next_painting_order[:howFarLook].count(painting)
        return count/20

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
        myInfo = [1]
        myInfo.append(my_bot_details['budget'] / 1001.0)
        myInfo.extend(self.get_need_want_pair(current_painting, my_bot_details['paintings']))

        #*** OTHER BOT DETAILS ***
        otherBotInfo = []
        # sort by currently closest to winning
        bots.sort(key=lambda x: (self.distanceToTargetDistributionMeasure(x['paintings']), random.random()), reverse=True)
        bots = bots[::-1]
        iter = 0
        i = -1
        while(iter < self.numInputCompetitors):
            i += 1 # always increment i
            if (i < len(bots)):
                bot = bots[i]
                if (bot['bot_name'] == self.name): # dont add self info again
                    continue
                if (bot['budget'] == 0): # dont care about broke bots
                    continue
                otherBotInfo.append(1) # bot exists
                otherBotInfo.append(bot['budget'] / 1001.0) # budget
                otherBotInfo.extend(self.get_need_want_pair(current_painting, bot['paintings']))
                iter += 1
            else:
                otherBotInfo.append(0) # bot doesnt exist
                otherBotInfo.append(0)
                otherBotInfo.extend([0,0])
                iter += 1


        #*** AUCTION DETAILS ***
        paintingsOrderNeedWantRarity = [] # includes current painting and next [paintingLookahead] paintings
        for i in range(self.paintingLookahead): # next x artists
            if (current_round + i >= len(painting_order)):
                paintingsOrderNeedWantRarity.extend([0,0,0])
                continue
            paintingsOrderNeedWantRarity.extend(self.get_need_want_pair(painting_order[current_round + i], bot['paintings']))
            paintingsOrderNeedWantRarity.append(self.get_painting_rarity(painting_order[current_round + i], painting_order[current_round + i + 1:]))

        #*** COMBINE ALL INTO INPUT ARRAY ***

        combinedNParr = np.concatenate([myInfo, otherBotInfo, paintingsOrderNeedWantRarity])
        #*** RESHAPE FOR INPUT TO MODEL ***
        modelInput = combinedNParr.reshape((1, len(combinedNParr)))

        #*** TARGET FOR NETWORK ***
        greedyBotBid = self.get_greedybot_bid(my_bot_details, current_painting)
        target = (greedyBotBid/250.0)

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
        self.model.save('RegressionBotSmall.keras')