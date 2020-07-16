import random

#------------------------------Dice Class------------------------------
#Images and current state data for a single die.
class Die:
    def __init__(self, imgArr): #Simple constructor
        self.cur_score = 0

    def roll(self):
        self.cur_score = random.randint(1,6) #Random no between 1 and 6 as those are the available scores on a standard die
        