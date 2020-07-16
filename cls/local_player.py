from .local_piece import LocalPlayer_Piece

#------------------------------Game Player Class------------------------------
#All data for a game player and its associated piece
class LocalPlayer:
    #Constructor for Player class
    #I'm going to guess this is relatively self-explanatory - it is called when the class in instantiated (creating an object) and sets up the instance variables of the new object
    def __init__(self, new_piece):
        self.local_piece = new_piece
    
    def getPiece(self):
        return self.local_piece
