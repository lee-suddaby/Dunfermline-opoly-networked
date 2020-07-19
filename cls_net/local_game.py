import numpy as np

from .local_board import LocalBoard
from .local_die import LocalDie
from .local_card_deck import LocalCard_Deck
from .local_player import LocalPlayer

#------------------------------Local Class------------------------------
#Stores images and other objects that cannot be passed over a network via Pyro4.
class LocalGame:
    def __init__(self, new_die, new_PL, new_CC, new_board, new_players):
        self.local_die = np.array(new_die) #Array of loaded pygame images
        self.local PL = np.array(new_PL)
        self.local_CC = np.array(new_CC)
        self.local_board = new_board
        self.local_players = new_players

    def getDieImg(self, score, die_num):
        return self.local_die[die_num].getImg(score)
        