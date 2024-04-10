import random

from keras import Sequential
from keras.layers import Dense
from keras.models import load_model
from keras import regularizers

import numpy as np
import get_state

class Bot(object):
    def __init__(self, copy, bot_id, Qref, verbose=1, loadModel="", epsilon = 0.1, alpha=1.0, epochStart=0, saveEvery = 5, mutationRate = 0, mutationSD = 0):
        self.name = (
            str(bot_id)  # Put your id number her. String or integer will both work
        )
        if (copy):
            return
        
        self.randomID = random.randint(1,100)

        self.Q_ref = Qref # reference to Q
        self.verbose = verbose

        self.upCount = 0
        self.downCount = 0

        if (loadModel==""):
            self.model = Sequential()
            self.model.add(Dense(units=20, activation='relu', input_dim=get_state.P_input_dimension, kernel_regularizer=regularizers.L2(1e-4)))
            self.model.add(Dense(units=10, activation='relu', kernel_regularizer=regularizers.L2(1e-4)))
            self.model.add(Dense(units=1, activation='sigmoid', kernel_regularizer=regularizers.L2(1e-4)))

            self.model.compile(optimizer='adam', loss='mse', metrics=['mae'])  # Use mean squared error for loss
        else:
            self.model = load_model(loadModel)

        if (mutationRate > 0 and mutationSD > 0):
            if (self.verbose == 1):
                print("Mutating...")
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

        self.batchX_list = [] # array of 'combinedNParr', the input info
        self.batchY_list = [] # array of 'greedyBotBidNORM', the target

        self.start_epoch = epochStart
        self.epoch = epochStart
        self.save_every = saveEvery

        self.epsilon = epsilon # how often a random action is performed
        self.alpha = alpha # how far the best action is pushed by Q_sa gradient

        self.reduce_every = 5
        for i in range(self.epoch // self.reduce_every):
            if (self.verbose == 1):
                print("Catch up reduce ", i+1)
            self.reduce_epsilon_alpha(0.95)


    def __deepcopy__(self, memo):
        # Create a new instance of the Bot class
        new_bot = Bot(True, self.name, self.Q_ref)  # Assuming 'name' is the only required attribute for initialization
        
        return new_bot


    def reduce_epsilon_alpha(self, factor):
        self.epsilon *= factor
        self.alpha *= factor
        if (self.verbose == 1):
            print("Eps, Alpha reduced by factor:",factor," new eps:", self.epsilon, " new alpha:", self.alpha)

    def qGradientAscent(self, steps, state, action):
        # Compute best action estimate using linear gradient ascent single step
        QsaGradEps = 1e-3
        for i in range(steps):
            Qsa = self.Q_ref.Q_sa(state, action)
            QsaEps = self.Q_ref.Q_sa(state, action + QsaGradEps)
            QsaGrad = (QsaEps - Qsa)/QsaGradEps
            action = action + self.alpha * QsaGrad

        return action

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
        p_action = self.model.predict(get_state.get_state_as_model_input(state), verbose=0)
        p_action = p_action[0][0] # Turn into actual float

        # epsilon exploration
        if (random.random() < self.epsilon):
            if (self.verbose == 1):
                print("Random action!")
            p_action = random.random()

        # Upload state-action pair to Q
        self.Q_ref.add_state_action_pair(state, p_action, my_bot_details['bot_unique_id'])

        # Store state where p action was taken
        self.batchX_list.append(state)

        # Compute best action estimate using linear gradient ascent 5 steps
        target_action = self.qGradientAscent(1, state, p_action)

        # Record up/down pushes for debug
        if (target_action > p_action):
            self.upCount += 1
        else:
            self.downCount += 1
        #print("Qsa",Qsa,"grad:",QsaGrad,"p_action",p_action,"\np_best_action",p_best_action_estimate,"Q[s,best a]",self.Q_ref.Q_sa(state, p_best_action_estimate))

        # Target action is best action estimate
        self.batchY_list.append(target_action)

        if (self.verbose == 1):
            print("p_action: ", p_action, "corr. bid:", get_state.actionToBid(p_action), "budget", my_bot_details['budget'])
        return min(get_state.actionToBid(p_action), my_bot_details['budget']) # bid action or as close to action as possible
    

    def discard_data(self):
        self.batchX_list = []
        self.batchY_list = []

    def fit_model(self, showEval = True):

        if (self.verbose <= 1):
            print("up count =", self.upCount, " down count =", self.downCount)
            self.upCount = 0
            self.downCount = 0

        # Convert batch lists to numpy arrays
        batchX_np = np.vstack(self.batchX_list)
        batchY_np = np.array(self.batchY_list)

        predictions = self.model.predict(batchX_np)
        mse = np.mean((np.array(predictions) - batchY_np) ** 2)
        # Print error
        if (showEval):
            print("Student bot, name:", self.name, "Epoch:", self.epoch, "Mean squared error:", mse)
        
        # Save every save_every batches, including initial model (epoch = 0)
        if (self.epoch % self.save_every == 0):
            self.saveModel(mse)

        if (self.epoch != self.start_epoch and self.epoch % self.reduce_every == 0):
            self.reduce_epsilon_alpha(0.92)

        # Fit the model with the batch data
        self.model.fit(batchX_np, batchY_np, epochs=self.epoch, batch_size=len(batchY_np), verbose=0)  # Adjust parameters as needed 
        self.epoch+=1

        # Clear batch lists ready for next
        self.batchX_list = []
        self.batchY_list = []


    def saveModel(self, mse):
        with open("Bot"+str(self.name)+"_mse_log.txt", "a") as file:
            file.write(f"epoch {self.epoch}: {mse}\n")
        self.model.save('BotDM'+self.name+"epoch"+str(self.epoch)+'.keras')
      