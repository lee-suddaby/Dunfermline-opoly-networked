#------------------------------Game_Controller Class------------------------------
#Used for storing the miscellaneous variables needed for controlling a player taking their turn
#Having them stored as part of the Game class means that moving to another screen does not allow the current player to restart their turn
class Game_Controller:
    def __init__(self):
        self.player_rolled = False #False if the player may roll
        self.card_used = True #Is only false if a card is available for use. True even if a card has not been drawn during a particular turn
        self.may_buy = False #True is player can buy a buyable property if they are on it
        self.turn_rent = 0
        self.cur_card_num = 0 #Pot Luck or Council Chest card drawn on a particular turn
        self.cur_card_deck = None #PL for Pot Luck and CC for Council Chest
        self.cur_doubles = 0
        self.roll_num1 = 0 #First dice num
        self.roll_num2 = 0 #Second dice num

    def reset(self):
        self.player_rolled = False
        self.card_used = True
        self.may_buy = False
        self.turn_rent = 0
        self.cur_card_num = 0
        self.cur_card_deck = None
        self.cur_doubles = 0
        self.roll_num1 = 0
        self.roll_num2 = 0
