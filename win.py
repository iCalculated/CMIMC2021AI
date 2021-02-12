
def win(history, remainingcards, score, hand, xbids, ybids): 
    if not remainingcards: 
        return history, score 
    card = remainingcards[0] 
    x, y = xbids[card - 2], ybids[card - 2] 
    tie = max(x, y) 
    giveuphand = deepcopy(hand) 
    mincard = min(hand) 
    giveuphand.remove(mincard) 
    giveuphistory = deepcopy(history) 
    giveuphistory.append(mincard) 
    if max(hand) <= tie: 
        return win(giveuphistory, remainingcards[1:], score, giveuphand, xbids, ybids) 
    else: 
        tryhand = deepcopy(hand) 
        tryhistory = deepcopy(history) 
        sorted(tryhand) 
        i = 0 
        while tryhand[i] <= tie: 
            i += 1 
        tryhistory.append(tryhand.pop(i)) 
        trybid = win(tryhistory, remainingcards[1:], score + card, tryhand, xbids, ybids) 
        giveupbid = win(giveuphistory, remainingcards[1:], score, giveuphand, xbids, ybids) 
        if trybid[1] > giveupbid[1]: 
            return trybid 
        else: 
            return giveupbid 

