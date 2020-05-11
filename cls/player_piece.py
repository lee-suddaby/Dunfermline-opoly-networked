#------------------------------Player Piece Class------------------------------
#Data etc. for interacting with the player's graphical token.
class Player_Piece:
    def __init__(self, new_x, new_y, new_img, new_num):
        self.x_pos = new_x
        self.y_pos = new_y
        self.piece_img = new_img
        self.piece_num = new_num #0-5, representing images with paths 'Pieces/<1-6>.png'. Used when saving player data.

    def getPieceImg(self): #Returns the image so it can be displayed on screen and move it when the player moves
        return self.piece_img

    def getX(self):
        return self.x_pos

    def getY(self):
        return self.y_pos
    
    def setX(self, newX):
        self.x_pos = newX

    def setY(self, newY):
        self.y_pos = newY