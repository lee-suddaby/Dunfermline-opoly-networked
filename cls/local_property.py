from enum import Enum
import numpy as np
import pygame

#------------------------------Property Superclass------------------------------
#Superclass for all board properties
#pType is currently used as an identifier:
#   Key is intergrated within the text file containing property data
class LocalProperty:
    def __init__(self, propName, ptype): #Basic constructor. 
        self.prop_title = propName #Property's name, as shown on board and title deed (if one exists)
        self.prop_type = ptype


#------------------------------Property Type Enumeration------------------------------
#Used for storing the different types of properties in a slightly more readable way than if numbers alone were used
class Prop_Type(Enum):
    NORMAL = 1
    SCHOOL = 2
    STATION = 3
    POT_LUCK = 4
    COUNCIL_CHEST = 5
    LOST_IN_BOGSIDE = 6
    GO_TO_BOGSIDE = 7
    PAYMENT = 8
    JOB_CENTRE = 9
    DISABLED_PARKING = 10
    
#------------------------------Normal Property Subclass------------------------------   
#Subclass of Property superclass
#Most common type of property on the board
#Can have upgrades purchased for it, and is part of a colour grouping
#Common Abbreviation: CH = Council House
#                       TB = Tower Block
class LocalNormal_Property(Property): #Create as subclass of Property
    #Constructor
    #Vals is an array where each element is one of the comma-separated values read on from the data file (where each property was stored on one line)
    def __init__(self, vals, new_deed, new_mdeed):
        Property.__init__(self, vals[0], Prop_Type.NORMAL) #Initialise superclass first with the two values it takes in its constructor
        self.title_deed = new_deed #Image storing the title deed for the property
        self.mortgage_deed = new_mdeed  #Image for the title deed to be shown when the property is mortgaged
        #Pygame colour linked to the group. 2 or 3 properties on the board will share one
        self.group_col = pygame.Color(int(vals[0]), int(vals[1]), int(vals[2]), 0) #Sets up the colour so that pygame recognises it as a RGB colour sequence, rather than an array of 3 numbers, as could potentially happen without
        
    def getTitleDeed(self):
        if self.mortgage_status:
            return self.mortgage_deed
        else:
            return self.title_deed

  
#------------------------------School Property Subclass------------------------------
#Another subclass of the Property superclass
#Schools determine rent based off of how many of them are owned by the one player
class LocalSchool_Property(Property):
    #Constructor - vals array works in the same way as it does for the NormalProperty class
    def __init__(self, vals, new_deed, new_mdeed):
        Property.__init__(self, vals[0], Prop_Type.SCHOOL) #Initialise superclass first
        self.title_deed = new_deed
        self.mortgage_deed = new_mdeed

    def getTitleDeed(self):
        if self.mortgage_status:
            return self.mortgage_deed
        else:
            return self.title_deed


#------------------------------Station Property Subclass------------------------------
#Another subclass of the property superclass
#This time, rents are determined based on the current score on the dice, and whether one or both stations are owned
class LocalStation_Property(Property):
    #Constructor - vals array works in the same way as it does for the NormalProperty class
    def __init__(self, vals, new_deed, new_mdeed):
        Property.__init__(self, vals[0], Prop_Type.STATION) #Initialise superclass first
        self.title_deed = new_deed
        self.mortgage_deed = new_mdeed

    def getTitleDeed(self):
        if self.mortgage_status:
            return self.mortgage_deed
        else:
            return self.title_deed
