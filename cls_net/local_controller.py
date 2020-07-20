#------------------------------Game_Controller Class------------------------------
#Used for storing the miscellaneous variables needed for controlling a player taking their turn
#Having them stored as part of the Game class means that moving to another screen does not allow the current player to restart their turn
class Local_Controller:
    def __init__(self):
        self.roll_img1 = None
        self.roll_img2 = None
        self.card_effs = [] #Integer effects of cur_card
        self.card_texts = [] #pygame-rendered texts telling the user the effects

    def reset(self):
        self.roll_img1 = None
        self.roll_img2 = None
        self.card_effs = []
        self.card_texts = []