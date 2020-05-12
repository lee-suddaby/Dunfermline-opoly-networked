import numpy as np

#------------------------------Card Class------------------------------
#Used for storing the individual Pot Luck and Council Chest cards
class Card:
    def __init__(self, new_name, new_img, new_effects, new_nums): #Constructor
        self.card_name = new_name #Pot Luck or Council Chest card
        self.card_img = new_img #Pygame surface object (i.e. image)
        self.card_effects = np.array(new_effects) #Array of strings storing textual descriptions of the effects of the cards. Will contain *'s which can be replaced with numbers from the following array
        self.card_nums = np.array(new_nums).astype(np.int) #Provides numerical values for the above effects. N.B. -1 will be used when an effect is not used