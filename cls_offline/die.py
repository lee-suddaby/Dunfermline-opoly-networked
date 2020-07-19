import numpy as np
import random

#------------------------------Dice Class------------------------------
#Images and current state data for a single die. Two instances will be used in the game
class Die:
    def __init__(self, imgArr): #Simple constructor
        self.cur_score = 0
        self.images = np.array(imgArr) #Array of loaded pygame images

    def getImg(self):
        return self.images[self.cur_score - 1] #-1 as indexing starts at 0; scores start at 1

    def roll(self):
        self.cur_score = random.randint(1,6) #Random no between 1 and 6 as those are the available scores on a standard die
        