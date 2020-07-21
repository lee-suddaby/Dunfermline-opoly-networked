import numpy as np

from .local_board import LocalBoard
from .local_die import LocalDie
from .local_card_deck import LocalCard_Deck
from .local_controller import Local_Controller
from .local_player import LocalPlayer

#------------------------------Local Class------------------------------
#Stores images and other objects that cannot be passed over a network via Pyro4.
class LocalGame:
    def __init__(self, new_die, new_PL, new_CC, new_board, new_players):
        self.die = np.array(new_die) #Array of loaded pygame images
        self.PL_Deck = np.array(new_PL)
        self.CC_Deck = np.array(new_CC)
        self.board = new_board
        self.players = new_players
        self.prop_thumbs = None
        self.controller = Local_Controller()

    def getDieImg(self, score, die_num):
        return self.die[die_num].getImg(score)
        
    def getPlayer(self, player_num):
        return self.players[player_num]
