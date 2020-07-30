import numpy as np

from .local_board import LocalBoard
from .local_die import LocalDie
from .local_card_deck import LocalCard_Deck
from .local_controller import Local_Controller
from .local_player import LocalPlayer

#------------------------------Local Class------------------------------
#Stores images and other objects that cannot be passed over a network via Pyro4.
class LocalGame:
    def __init__(self, new_die, new_board, new_players, new_this_player):
        self.die = np.array(new_die) #Array of loaded pygame images
        self.board = new_board
        self.players = new_players
        self.prop_thumbs = None
        self.controller = Local_Controller()
        self.this_player_num = new_this_player #Each player will have their own LocalGame on their machine. 
        # This attribute stores the number of their player (i.e. so their is some record of the player on this machine
        # being player 2, for example).

    def getDieImg(self, score, die_num):
        return self.die[die_num].getImg(score)
        
    def getPlayer(self, player_num):
        return self.players[player_num]
