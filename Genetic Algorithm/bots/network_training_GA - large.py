import random

from keras import Sequential
from keras.layers import Dense
from keras.models import load_model

import numpy as np

import sys
import time

class Bot(object):
    def __init__(self, bot_id, loadModel=""):
        self.name = (
            str(bot_id)  # Put your id number her. String or integer will both work
        )
        self.randomID = random.randint(1,1000)
        self.paintingLookahead = 10

        self.model = Sequential()
        if (loadModel == ""):
            self.model.add(Dense(units=64, activation='relu', input_dim=(180+(4*self.paintingLookahead))))
            self.model.add(Dense(units=10, activation='relu'))
            self.model.add(Dense(units=1, activation='sigmoid'))
            self.model.compile(optimizer='adam', loss='mse', metrics=['mae'])  # Use mean squared error for loss
        else:
            self.model = load_model(loadModel)

        self.myInfo = []


    def replaceModelWithChild(self, parent1, parent2, mutationRate, mutationSD):
        self.randomID = random.randint(1,100)

        # parents have child
        for i in range(len(parent1.layers)):
            layer1 = parent1.layers[i]
            layer2 = parent2.layers[i]
            layerC = self.model.layers[i]
            if hasattr(layer1, 'get_weights'):
                weights1 = layer1.get_weights()
                weights2 = layer2.get_weights()
                child_weights = []
                for j in range(len(weights1)):
                    w1 = weights1[j]
                    w2 = weights2[j]
                    shape = w1.shape
                    parentMask = np.random.rand(*shape) < 0.5
                    child_w = np.where(parentMask, w1, w2)
                    child_weights.append(child_w)
                layerC.set_weights(child_weights)

        # mutate some parts of child
        for layer in self.model.layers:
            if hasattr(layer, 'get_weights'):
                weights = layer.get_weights()
                mutated_weights = []
                for w in weights:
                    shape = w.shape
                    mutation_mask = np.random.rand(*shape) < mutationRate
                    mutation_values = np.random.normal(0, mutationSD, size=shape)
                    mutated_w = np.where(mutation_mask, w + mutation_values, w)
                    mutated_weights.append(mutated_w)
                layer.set_weights(mutated_weights)


    def replaceModel(self, newModel, mutationRate, mutationSD):
        self.randomID = random.randint(1,100)

        self.model = newModel

        for layer in self.model.layers:
            if hasattr(layer, 'get_weights'):
                weights = layer.get_weights()
                mutated_weights = []
                for w in weights:
                    shape = w.shape
                    mutation_mask = np.random.rand(*shape) < mutationRate
                    mutation_values = np.random.normal(0, mutationSD, size=shape)
                    mutated_w = np.where(mutation_mask, w + mutation_values, w)
                    mutated_weights.append(mutated_w)
                layer.set_weights(mutated_weights)

    def __deepcopy__(self, memo):
        # Create a new instance of the Bot class
        new_bot = Bot(self.name)  # Assuming 'name' is the only required attribute for initialization
        
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

    def distanceToTargetDistributionMeasure(self, paintings):
        artistValues= paintings.values()
        sortedArtistValues = sorted(artistValues)[::-1]
        difference = max(3 - sortedArtistValues[0], 0)
        difference += max(3 - sortedArtistValues[1], 0)
        difference += max(1 - sortedArtistValues[2], 0)
        difference += max(1 - sortedArtistValues[3], 0)
        return difference

    def scoreState(self, my_bot_details, all_budgets_zero):


        budget = my_bot_details['budget']
        artistValues= my_bot_details['paintings'].values()
        #sortedArtistValues = sorted(artistValues)[::-1]
        if (all_budgets_zero):
            print("All budgets 0, both score 0. Artist values:",artistValues)
            return 0

        difference = self.distanceToTargetDistributionMeasure(my_bot_details['paintings'])

        if (difference == 0):
            print("Winner, name:",self.name, "paintings:", artistValues, "budget:", budget)
            return 11 - 5*(budget/1001)
        print("Loser, name:",self.name, "paintings:", artistValues, "budget:", budget)

        score = 6 - (difference*0.5) - 2*(budget/1001)
        if (budget == 0):
            score = 0 # no score if run out of money
        return score
    
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

        #print(self.name, "bids", bid)
        return min(bid, my_bot_details['budget'])        