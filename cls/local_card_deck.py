import numpy as np
import random

#------------------------------Card Deck Class------------------------------
#Used for storing a deck of Pot Luck or Council Chest Cards; each card is of the Card class
class LocalCard_Deck:
    def __init__(self, cardArr): #Simple constructor
        self.card_arr = np.array(cardArr)

    def getCard(self, num):
        return self.card_arr[num]