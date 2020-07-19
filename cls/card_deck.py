import numpy as np
import random

#------------------------------Card Deck Class------------------------------
#Used for storing a deck of Pot Luck or Council Chest Cards; each card is of the Card class
class Card_Deck:
    def __init__(self, number_of_cards): #Simple constructor
        self.card_arr = list(range(0, number_of_cards-1))
        self.deck_pointer = 0 #Stores which element of the array contains the card that should be presented to a player next

    def getNextCardNum(self):
        ret_num = self.card_arr[self.deck_pointer] #Don't return yet as pointer must still be incremented
        self.deck_pointer += 1
        if self.deck_pointer > len(self.card_arr)-1: #-1 as len gives number of discrete elements but first element is indexed zero
            self.deck_pointer = 0
        return ret_num

    def shuffleCards(self): #Makes used of the Knuth Shuffle alrogithm (aka Fisher-Yates shuffle)
        for outer in range(len(self.card_arr)-1, 0, -1):
            rand = random.randrange(outer + 1) #Random index to swap with current element
            self.card_arr[outer], self.card_arr[rand] = self.card_arr[rand], self.card_arr[outer] #Python-specific way of swapping two items without the use of a temp variable
