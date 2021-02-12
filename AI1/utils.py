class winner_bot:
    def __init__(self):
        # You can define global states (that last between moves) here

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

        print(f"{self.bids}")
        print(f"{self.bids[card]}")
        return self.bids[card]
        
        #print(f"{self.past=}")

        if card == 14: return 2
        return card + 1

    def calculate_thresholds(self):
        for card, bids in self.past.items():
            self.win[card].append(max(bids[-1]) + 1)
            self.tie[card].append(max(bids[-1]) if bids[-1][0] != bids[-1][1] else 0)

    def calculate_sequence(self):
        #self.bids has things
        options = list(range(2,15))
        droplist = [] 
        #for card, bid in self.tie.items():
            #if bid == 0:
                #droplist.append(card)
        for card in range(14,1,-1):
            winners = list(filter(lambda x: x >= self.win[card][-1], options))
            if winners:
                bid = max(winners)
                self.bids[card] = bid
                options.remove(bid)
            else:# self.tie[card] == 0:
                self.bids[card] = options.pop(0)

            

class one_up_plus_bot:
    def move(self, hand, others, card, scores):
        if card == 14: return 14
        elif card == 13: return 2
        return card + 1

class mirror_bot:
    def move(self, hand, others, card, scores):
        return card

class one_up_bot:
    def move(self, hand, others, card, scores):
        if card == 14: return 2
        return card + 1

class plus_four_bot:
    def move(self, hand, others, card, scores):
        return list(range(2,15))[(card+2)%13]

class broken_mirror_bot:
    def move(self, hand, others, card, scores):
        if card > 8:
            return card - 1
        elif card == 8:
            return 14
        else:
            return card

class countdown_bot:
    def move(self, hand, others, card, scores):
        return max(hand)

class countup_bot:
    def move(self, hand, others, card, scores):
        return min(hand)

class random_bot:
    def move(self, hand, others, card, scores):
        return random.choice(hand)
class info_bot:
    def __init__(self):
        # You can define global states (that last between moves) here
        self.past = defaultdict(list)
        self.other_hands = []
        self.previous_auction = -1
        pass
    
    # others: list of lists, each list has hand
    def move(self, hand, others, card, scores):
        past_cards = []
        if len(hand) != 13:
            for curr, prev in zip(others, self.other_hands[-1]):
                past_cards.extend(set(prev).difference(set(curr))) 
            self.past[self.previous_auction].append(past_cards)
        if len(hand) == 1: self.past[card].append([x for sub in others for x in sub])
        
        self.previous_auction = card
        self.other_hands.append(copy.deepcopy(others))
        
        print(f"{self.past=}")

        if card == 14: return 2
        return card + 1
