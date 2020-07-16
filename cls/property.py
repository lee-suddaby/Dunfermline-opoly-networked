from enum import Enum
import numpy as np
import pygame

#------------------------------Property Superclass------------------------------
#Superclass for all board properties
#pType is currently used as an identifier:
#   Key is intergrated within the text file containing property data
class Property:
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
class Normal_Property(Property): #Create as subclass of Property
    #Constructor
    #Vals is an array where each element is one of the comma-separated values read on from the data file (where each property was stored on one line)
    def __init__(self, vals):
        Property.__init__(self, vals[0], Prop_Type.NORMAL) #Initialise superclass first with the two values it takes in its constructor
        self.cost = int(vals[1])
        self.rentNo = int(vals[2])
        self.rentCH = np.array([0] * 4)
        for counter in range(4): #Array to represent the rents with 1 to 4 Council Houses. Easier than 4 separate variables
            self.rentCH[counter] = int(vals[counter+3])
        self.rentTB = int(vals[7])
        self.CH_cost = int(vals[8])
        self.TB_cost = int(vals[9])
        self.mortgage_val = int(vals[10])
        self.C_Houses = 0
        self.T_Blocks = 0
        self.prop_owner = -1 #Numerical identifier of the player who owns it. -1 if unowned
        self.mortgage_status = False #Boolean for whether the property is mortgaged or not. False = not mortgaged

    #Determine how much rent should be paid based on CH and TB owned
    def getRent(self):
        if self.mortgage_status: #No rent if property is mortgaged
            return 0
        if self.C_Houses == 0:
            return self.rentNo
        elif self.T_Blocks != 0:
            return self.rentTB
        elif self.T_Blocks == 0:
            return self.rentCH[self.C_Houses-1] #-1 as first element is at position 0
        
    def buyCH(self):
        if self.C_Houses < 4: #Max 4 CH
            self.C_Houses = self.C_Houses + 1

    def buyTB(self):
        if self.C_Houses < 4: #4 CH must be owned to purchase hotel
            pass
        else:
            self.T_Blocks += 1

    def sellCH(self):
        if self.C_Houses > 0 and self.T_Blocks == 0:
            self.C_Houses -= 1

    def sellTB(self):
        if self.T_Blocks > 0:
            self.T_Blocks -= 1
    
    def buyProperty(self, newOwner):
        if self.prop_owner == -1: #Property can only be bought if no one owns it yet
            self.prop_owner = newOwner

  
#------------------------------School Property Subclass------------------------------
#Another subclass of the Property superclass
#Schools determine rent based off of how many of them are owned by the one player
class School_Property(Property):
    #Constructor - vals array works in the same way as it does for the NormalProperty class
    def __init__(self, vals):
        Property.__init__(self, vals[0], Prop_Type.SCHOOL) #Initialise superclass first
        self.cost = int(vals[1])
        self.mortgage_val = int(vals[6])
        self.rent_vals = np.array([0] * 4)
        for counter in range(4):
            self.rent_vals[counter] = int(vals[counter+2])
        self.prop_owner = -1
        self.mortgage_status = False

    def getRent(self, board, playerNo): #propArr is an array of Property classes (including subclasses of it)
        #Counting occurrences algorithm, to count how many schools (including this one) are owned by a specific player
        if self.mortgage_status: #Mortgaged properties do not collect rent
            return 0
        
        rent_count = 0
        for counter in range(board.max_pos + 1):
            if board.getProp(counter).prop_type == Prop_Type.SCHOOL:
                if board.getProp(counter).prop_owner == playerNo:            
                    rent_count = rent_count + 1
        return self.rent_vals[rent_count-1] #-1 as array is zero-indexed

    def buyProperty(self, newOwner):
        if self.prop_owner == -1: #Property can only be bought if no one owns it yet
            self.prop_owner = newOwner


#------------------------------Station Property Subclass------------------------------
#Another subclass of the property superclass
#This time, rents are determined based on the current score on the dice, and whether one or both stations are owned
class Station_Property(Property):
    #Constructor - vals array works in the same way as it does for the NormalProperty class
    def __init__(self, vals):
        Property.__init__(self, vals[0], Prop_Type.STATION) #Initialise superclass first
        self.cost = int(vals[1])
        self.mortgage_val = int(vals[4])
        self.rent_mods = np.array([0] * 2)
        for counter in range(2):
            self.rent_mods[counter] = int(vals[counter+2])
        self.prop_owner = -1
        self.mortgage_status = False

    def getRent(self, board, playerNo, diceRoll): #propArr is an array of Property classes (including subclasses of it)
        #Counting occurrences algorithm, to count how many schools (including this one) are owned by a specific player
        if self.mortgage_status: #Mortgaged properties do not collect rent
            return 0
        
        rent_count = 0
        for counter in range(board.max_pos + 1):
            if board.getProp(counter).prop_type == Prop_Type.STATION:
                if board.getProp(counter).prop_owner == playerNo:            
                    rent_count = rent_count + 1
        #Rent for a station property is dependent on the dice roll, as well as how many of the two are owned
        return self.rent_mods[rent_count-1] * diceRoll #-1 as array is zero-indexed

    def buyProperty(self, newOwner):
        if self.prop_owner == -1: #Property can only be bought if no one owns it yet
            self.prop_owner = newOwner

#------------------------------Charge Property Subclass------------------------------ 
#Any property on the board that charges the player money when they land on it
class Charge_Property(Property):
    def __init__(self, new_title, new_charge):
        Property.__init__(self, new_title, Prop_Type.PAYMENT) #Initialise superclass first
        self.surcharge = int(new_charge)
    
    def getCharge(self):
        return self.surcharge


#------------------------------Go To Bogside Property Subclass------------------------------ 
#Sends the player to the would-be jail (called Lost in Bogside in this version)
class Go_To_Bogside(Property):
    def __init__(self, new_title, new_pos):
        Property.__init__(self, new_title, Prop_Type.GO_TO_BOGSIDE) #Initialise superclass first
        self.bogside_pos = new_pos
    
    def getBogsidePos(self):
        return self.bogside_pos