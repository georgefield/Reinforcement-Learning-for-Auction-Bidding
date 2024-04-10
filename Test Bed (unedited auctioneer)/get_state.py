import numpy as np
import random
import math

painting_look_ahead = 5
num_other_competitors_in_state = 2
P_input_dimension = 4+(4*num_other_competitors_in_state)+(3*painting_look_ahead)

# More action values lie inside reasonable range, allows networks to be more fine
def actionToBid(x):
    out = round( 250 * ((x - 0.5)**3 + 0.5 * (x - 0.5) + 3/8) * (4/3) )
    return out

#*** Functions needed for get_state ***
def distanceToTargetDistributionMeasure(paintings):
    artistValues= paintings.values()
    sortedArtistValues = sorted(artistValues)[::-1]
    difference = max(3 - sortedArtistValues[0], 0)
    difference += max(3 - sortedArtistValues[1], 0)
    difference += max(1 - sortedArtistValues[2], 0)
    difference += max(1 - sortedArtistValues[3], 0)
    return difference

def get_need_want_pair(current_painting, paintings_i_have):
    if (paintings_i_have[current_painting] == 0 or paintings_i_have[current_painting] == 2):
        return [1,0]
    if (paintings_i_have[current_painting] == 1):
        return [0,1]
    return [0,0]

def get_painting_rarity(painting, next_painting_order):
    howFarLook = min(len(next_painting_order), 20)
    count = next_painting_order[:howFarLook].count(painting)
    return count/20
#*** ***

# Encodes the current agent state as a vector of values in [0,1]
def get_state(  current_round,
                bots,
                painting_order,
                my_bot_details,
                current_painting
    ):

    #*** MY BOT DETAILS ***
    myInfo = [1]
    myInfo.append(my_bot_details['budget'] / 1001.0)
    myInfo.extend(get_need_want_pair(current_painting, my_bot_details['paintings']))

    #*** OTHER BOT DETAILS ***
    otherBotInfo = []
    # sort by currently closest to winning
    bots.sort(key=lambda x: (distanceToTargetDistributionMeasure(x['paintings']), random.random()), reverse=True)
    bots = bots[::-1]
    iter = 0
    i = -1
    while(iter < num_other_competitors_in_state):
        i += 1 # always increment i
        if (i < len(bots)):
            bot = bots[i]
            if (bot['bot_name'] == my_bot_details['bot_name']): # dont add self info again
                continue
            if (bot['budget'] == 0): # dont care about broke bots
                continue
            otherBotInfo.append(1) # bot exists
            otherBotInfo.append(bot['budget'] / 1001.0) # budget
            otherBotInfo.extend(get_need_want_pair(current_painting, bot['paintings']))
            iter += 1
        else:
            otherBotInfo.append(0) # bot doesnt exist
            otherBotInfo.append(0)
            otherBotInfo.extend([0,0])
            iter += 1

    #*** AUCTION DETAILS ***
    paintingsOrderNeedWantRarity = [] #includes current painting and next [paintingLookahead] paintings
    for i in range(painting_look_ahead): # next x artists
        if (current_round + i >= len(painting_order)):
            paintingsOrderNeedWantRarity.extend([0,0,0])
            continue
        paintingsOrderNeedWantRarity.extend(get_need_want_pair(painting_order[current_round + i], my_bot_details['paintings']))
        paintingsOrderNeedWantRarity.append(get_painting_rarity(painting_order[current_round + i], painting_order[current_round + i:]))

    #*** COMBINE ALL INTO INPUT ARRAY ***
    return myInfo + otherBotInfo + paintingsOrderNeedWantRarity


def get_state_as_model_input(state_list):
    stateNP = np.array(state_list)
    return stateNP.reshape((1, len(stateNP)))

def get_state_action_as_model_input(state_list, action):
    stateNP = np.array(state_list)
    stateActionNP = np.append(stateNP, action)
    return stateActionNP.reshape((1, len(stateActionNP)))