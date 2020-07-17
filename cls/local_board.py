import pygame
import numpy as np
from .local_property import Prop_Type

#------------------------------Board Class------------------------------
#Used for storing all data for properties, the two decks of cards, as well as a few other pieces of information such as money collected on passing the Job Centre
class LocalBoard:
    def __init__(self, new_props, new_PL, new_CC, new_img, new_sf): #Constructor
        self.properties = np.array(new_props) #Objects of various subclasses of the Property superclass
        self.max_pos = len(new_props) - 1 #Highest position (when zero-indexed) that a player can be on; also highest indexed element in properties array
        self.PL_Deck = new_PL #Card_Deck object
        self.CC_Deck = new_CC #Card_Deck object
        self.board_img = pygame.transform.smoothscale(new_img, [int(768*new_sf), int(768*new_sf)]) #Pygame image of the actual board - the one that is displayed on screen
        self.board_sf = new_sf #Mainly used in determining the pieces' positions on the board; this was only optimised for a 768x768 board, so any other size requires this value to be scaled slightly

    def getProp(self,b_pos):
        return self.properties[b_pos]
        #Checks if the group to which a certain property belongs 

    #Counts the number of properties that are a memeber of a certain property's 'colour group'
    def countGroupSize(self, player_num, prop_num):
        if self.getProp(prop_num).prop_type != Prop_Type.NORMAL: #Only NORMAL properties have a colour group
            return 0
        group_count = 0
        find_col = self.getProp(prop_num).group_col #Colour of the group which we are concerned with
        for counter in range(self.max_pos + 1):
            if self.getProp(counter).prop_type == Prop_Type.NORMAL: #Prevents errors as no other types have a Group Colour
                if self.getProp(counter).group_col == find_col and self.getProp(counter).prop_owner == player_num:
                    group_count += 1
        return group_count

    def getPLImg(self, card_num):
        return self.PL_Deck[card_num]
    
    def getCCImg(self, card_num):
        return self.CC_Deck[card_num]