import numpy as np

#------------------------------Dice Class------------------------------
#Images and current state data for a single die.
class LocalDie:
    def __init__(self, imgArr): #Simple constructor
        self.images = np.array(imgArr) #Array of loaded pygame images

    def getImg(self, score):
        return self.images[score - 1] #-1 as indexing starts at 0; scores start at 1
        