#------------------------------Player Piece Class------------------------------
#Data etc. for interacting with the player's graphical token.
class LocalPlayer_Piece:
    def __init__(self, new_x, new_y, new_img, new_num):
        self.piece_x = new_x
        self.piece_y = new_y
        self.piece_img = new_img #Stores the image that will be displayed on screen.
        self.piece_num = new_num #0-5, representing images with paths 'Pieces/<1-6>.png'. Used when saving player data.