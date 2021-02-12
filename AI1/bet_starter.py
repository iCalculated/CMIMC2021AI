# Bet Starter File

# NOTE: You can run this file locally to test if your program is working.

#=============================================================================

# INPUT FORMAT: hand, others, card, scores

# hand: Your current hand (a list of integers 2 to 14)
# others: All other players' hands, in a fixed order
# card: The card currently being bet on (an integer 2 to 14)
# scores: All current scores of players (from this game only) in a
#   fixed order. Your score is displayed as the first value.

# Example Input:

# hand: [2, 4, 14]
# others: [[6, 8, 9], [5, 11, 13]]
# card: 9
# scores: [34, 21, 18]

#=============================================================================

# OUTPUT FORMAT: A single integer between 2 and 14, inclusive, that is
# currently in your hand.

# Invalid outputs will result in your lowest card being played by default.

### WARNING: COMMENT OUT YOUR DEBUG/PRINT STATEMENTS BEFORE SUBMITTING !!!
### (this file uses standard IO to communicate with the grader!)

#=============================================================================

# Write your bot in the bet_bot class. Helper functions and standard library
# modules are allowed, and can be written before/inside these classes.

# You can define as many different strategies as you like, but only the class
# currently named "bet_bot" will be run officially.


# Example bot that plays a random card every round:

import random
from collections import defaultdict
import copy

class bet_bot:
    
    def __init__(self):
        self.past = defaultdict(list)
        self.other_hands = []
        self.previous_auction = -1
        self.win = defaultdict(list)
        self.tie = defaultdict(list)
        self.bids = defaultdict(int)
    
    # others: list of lists, each list has hand
    def move(self, hand, others, card, scores):
        if len(self.past) >= 13 and len(hand)==13:
            self.calculate_thresholds()
            self.calculate_sequence()

        past_cards = []
        if len(hand) != 13:
            for curr, prev in zip(others, self.other_hands[-1]):
                past_cards.extend(set(prev).difference(set(curr))) 
            self.past[self.previous_auction].append(past_cards)
        if len(hand) == 1: 
            self.past[card].append([x for sub in others for x in sub])
        
        self.previous_auction = card
        self.other_hands.append(copy.deepcopy(others))

        return self.bids[card]
        
        if card == 14: return 2
        return card + 1

    def calculate_thresholds(self):
        for card, bids in self.past.items():
            self.win[card].append(max(bids[-1]) + 1)
            self.tie[card].append(max(bids[-1]) if bids[-1][0] != bids[-1][1] else 0)

    def calculate_sequence(self):
        options = list(range(2,15))
        for card in range(14,1,-1):
            winners = list(filter(lambda x: x >= self.win[card][-1], options))
            if winners:
                bid = max(winners)
                self.bids[card] = bid
                options.remove(bid)
            else:# self.tie[card] == 0:
                self.bids[card] = options.pop(0)

#=============================================================================

# Local testing parameters

# If you would like to view a turn by turn game display while testing locally,
# set this parameter to True

LOCAL_VIEW = True

# Set a list of 3 strategies you would like to test locally

LOCAL_STRATS = [one_up_plus_bot(), random_bot(), bet_bot()]

#=============================================================================












































# You don't need to change any code below this point

import json
import sys

def WAIT():
    return json.loads(input())

def SEND(data):
    print(json.dumps(data), flush=True)

MASK = lambda a,i: a[:i] + a[i+1:]

def PLAY(players):
    scores = [0] * 3
    hands = [[*range(2, 15)] for i in range(3)]
    deck = [*range(2, 15)]
    for _ in range(13):
        card = random.choice(deck)
        deck.remove(card)
        if LOCAL_VIEW:
            for i in range(3):
                print(f"Player {i+1}'s hand:", ' '.join(map(str, hands[i])))
            print("Card being bet on:", card)
        values = []
        for i in range(3):
            try:
                val=players[i].move(hands[i],MASK(hands,i),card,[scores[i]]+MASK(scores,i))
                if not (val==int(val) and val in hands[i]):
                    raise Exception('invalid move')
            except Exception as e:
                print(f"Player {i+1} has an error: {e}! Playing the lowest card instead.")
                val = min(hands[i])
            values.append(val)
            if LOCAL_VIEW:
                print(f"Player {i+1}'s bet:", val)
        for i in range(3):
            hands[i].remove(values[i])
        big = max(values)
        if values.count(big) == 1:
            if LOCAL_VIEW:
                print(f"Player {values.index(big)+1} has won the card!")
            scores[values.index(big)] += card
        else:
            if LOCAL_VIEW:
                print("There was a tie! Nobody won the card.")
        if LOCAL_VIEW:
            print("Current totals:", ' '.join(map(str, scores)))
            print()
            input("Enter to continue (change LOCAL_VIEW to toggle this)")
    print("Game finished!")
    print("Final totals:",' '.join(map(str, scores)))
    if not LOCAL_VIEW:
        print("Change LOCAL_VIEW to True to see a turn by turn replay")

if len(sys.argv) < 2 or sys.argv[1] != 'REAL':
    PLAY(LOCAL_STRATS)
    input()

else:
    player = bet_bot()
    while True:
        data = WAIT()
        play = player.move(data["hand"],data["others"],data["card"],data["scores"])
        SEND(play)
