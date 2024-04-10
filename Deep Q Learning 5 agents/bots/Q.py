import random

from keras import Sequential
from keras.layers import Dense
from keras.models import load_model
from keras import regularizers

import numpy as np
import get_state

class Q(object):
    def __init__(self, epochStart=0, saveEvery = 5, load_existing_model=""):

        if (load_existing_model == ""):
            self.model = Sequential()
            self.model.add(Dense(units=20, activation='relu', input_dim=(get_state.P_input_dimension + 1), kernel_regularizer=regularizers.L2(1e-3)))
            self.model.add(Dense(units=10, activation='relu', kernel_regularizer=regularizers.L2(1e-3)))
            self.model.add(Dense(units=1, activation='sigmoid', kernel_regularizer=regularizers.L2(1e-3)))

            self.model.compile(optimizer='adam', loss='mse', metrics=['mae'])  # Use mean squared error for loss
        else:
            self.model = load_model(load_existing_model)

        self.epoch = epochStart
        self.save_every = saveEvery

        self.state_action_pairs = {}

        self.batchX_list = []
        self.batchY_list = []

    # Get evaluation of state-action
    def Q_sa(self, state, action):
        return self.model.predict(get_state.get_state_action_as_model_input(state, action), verbose=0)


    def add_state_action_pair(self, state, action, botIdStr):
        if botIdStr not in self.state_action_pairs.keys():
            self.state_action_pairs[botIdStr] = []
        # Use copy to avoid bugs
        stateAndAction = state.copy()
        stateAndAction.append(action)
        self.state_action_pairs[botIdStr].append(stateAndAction)


    def finish_round(self, winnerIdStr, batchDone = True, showEval = True):
        
        print("Q.finish_round(), winner id:", winnerIdStr, "batch done:",batchDone)

        # On round finish transfer data to from state_action_pairs to batchX and add to batchY 1s or 0s depending on if that state-action pairs went on to win
        for botIdStr in self.state_action_pairs.keys():
            self.batchX_list.append(self.state_action_pairs[botIdStr])
            if (botIdStr == winnerIdStr):
                self.batchY_list.extend([[1]] * len(self.state_action_pairs[botIdStr]))
            else:
                self.batchY_list.extend([[0]] * len(self.state_action_pairs[botIdStr]))

        self.state_action_pairs = {}

        if (batchDone):

            batchX_np = np.vstack(self.batchX_list)  # Convert batchX_list to NumPy array
            batchY_np = np.vstack(self.batchY_list)  # Convert batchY_list to NumPy array

            predictions = self.model.predict(batchX_np)
            mse = np.mean((np.array(predictions) - batchY_np) ** 2)
            # Print error
            if (showEval):
                print("Q model, epoch:", self.epoch, "Mean squared error:", mse)

            # Save every save_every batches, including initial model (epoch = 0)
            if (self.epoch % self.save_every == 0):
                self.saveModel(mse)

            self.model.fit(batchX_np, batchY_np, epochs=self.epoch, batch_size=len(batchX_np), verbose=0)
            self.epoch += 1
            
            self.batchX_list = []
            self.batchY_list = []


    def saveModel(self, mse):
        with open("Q_mse_log.txt", "a") as file:
            file.write(f"epoch {self.epoch}: {mse}\n")
        self.model.save('Qepoch'+str(self.epoch)+'.keras')
