import numpy as np

#------------------------------Local Class------------------------------
#Stores images and other objects that cannot be passed over a network via Pyro4.
class LocalGame:
    def __init__(self, new_die, new_PL, new_CC, new_board, new_players):
        self.local_die = np.array(imgArr) #Array of loaded pygame images
        self.local PL = np.array(PLArr)
        self.local_CC = np.array(CCArr)
        self.local_board = new_board
        self.local_players = new_players

    def getDieImg(self, score):
        return self.die_images[die_score - 1]
    
    def getPLImg(self, card_num):
        return self.PL_deck_img[card_num]
    
    def getCCImg(self, card_num):
        return self.PL_deck_img[card_num]
        