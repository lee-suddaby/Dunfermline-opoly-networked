from .local_piece import LocalPlayer_Piece

#------------------------------Game Player Class------------------------------
#All data for a game player and its associated piece
class LocalPlayer:
    #Constructor for Player class
    #I'm going to guess this is relatively self-explanatory - it is called when the class in instantiated (creating an object) and sets up the instance variables of the new object
    def __init__(self, new_num, new_piece):
        self.player_num = new_num
        self.player_piece = new_piece
