import random

from keras import Sequential
from keras.layers import Dense
from keras.models import load_model
from keras import regularizers

import numpy as np

import sys
import time
import get_state

class Bot(object):
    def __init__(self, bot_id, loadModel="", copy=False):
        self.name = (
            str(bot_id)  # Put your id number her. String or integer will both work
        )
        if (copy):
            return
        
        self.randomID = random.randint(1,100000)

        if (loadModel == ""):
            self.model = Sequential()
            self.model.add(Dense(units=20, activation='relu', input_dim=get_state.P_input_dimension, kernel_regularizer=regularizers.L2(1e-4)))
            self.model.add(Dense(units=10, activation='relu', kernel_regularizer=regularizers.L2(1e-4)))
            self.model.add(Dense(units=1, activation='sigmoid', kernel_regularizer=regularizers.L2(1e-4)))

            self.model.compile(optimizer='adam', loss='mse', metrics=['mae'])  # Use mean squared error for loss
        else:
            self.model = load_model(loadModel)


    def __deepcopy__(self, memo):
        # Create a new instance of the Bot class
        new_bot = Bot(self.name,"",True)  # Assuming 'name' is the only required attribute for initialization
        
        return new_bot


    def replaceModelWithChild(self, parent1, parent2, mutationRate, mutationSD):
        self.randomID = random.randint(1,100000)

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
        self.randomID = random.randint(1,100000)

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
        p_action = self.model.predict(get_state.get_state_as_model_input(state), verbose=0)[0][0]

        bid = get_state.actionToBid(p_action)

        return min(bid, my_bot_details['budget'])        
    
    # Needed to score state
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

        if (all_budgets_zero): # both had run out of budget before end
            print("All budgets 0, both score 0. Artist values:",artistValues)
            return 0

        difference = self.distanceToTargetDistributionMeasure(my_bot_details['paintings'])

        if (difference == 0):
            print("Winner, name:",self.name, "paintings:", artistValues, "budget:", budget)
            return 12
        
        print("Loser, name:",self.name, "paintings:", artistValues, "budget:", budget)
        score = 8 - difference
        if (budget == 0):
            score *= 0.5 # penalise running out of money more
        return score