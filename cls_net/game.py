import numpy as np
import pygame
import Pyro4
from .property import Prop_Type
from .game_controller import Game_Controller
from .lobby import Lobby

#------------------------------Game Class------------------------------
#Brings all the game data together into one cohesive object that can be controlled more easily than all other data/objects independently
@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Game:
    def __init__(self):
        self.lobby = Lobby()

    def setupGame(self, new_players, new_dice, new_board):
        self.players = np.array(new_players) #The 2-6 players of the game
        self.dice = np.array(new_dice) #Game's two dice
        self.cur_player_num = 0 #Index of current player in he players array
        self.board = new_board
        self.controller = Game_Controller()

    def getCurPlayerNum(self):
        return self.cur_player_num
    
    def getCurProp(self):
        return self.board.getProp(self.players[self.cur_player_num].player_pos)

    def getCurPropNum(self):
        return self.players[self.cur_player_num].player_pos

    def getCurPropOwner(self):
        return self.board.properties[self.players[self.cur_player_num].player_pos].prop_owner

    def getCurPropType(self):
        return self.board.properties[self.players[self.cur_player_num].player_pos].prop_type

    def advancePlayer(self): #Next player's turn
        self.cur_player_num += 1
        self.controller.reset()
        if self.cur_player_num > len(self.players)-1:
            self.cur_player_num = 0 #Restart from first player
        if self.players[self.cur_player_num].player_turnsToMiss > 0 or self.players[self.cur_player_num].player_active == False:
            if self.players[self.cur_player_num].player_turnsToMiss > 0:
                self.players[self.cur_player_num].setMissTurns(self.players[self.cur_player_num].player_turnsToMiss - 1) #Player is skipped; the number of turns still to be missed decrements
            self.advancePlayer() #Recursively call function to try and advance to the player after the one missing a turn

    def getPlayer(self, p_num): #Return a specific player
        return self.players[p_num]

    def countActivePlayers(self): #Number of players that have not yet gone bankrupt
        ret_count = 0
        for counter in range(len(self.players)): #All players, active or not
            if self.players[counter].player_active:
                ret_count += 1
        return ret_count

    def determineRent(self, player_num):
        ret_rent = 0
        if self.board.getProp(self.players[player_num].player_pos).prop_type == Prop_Type.NORMAL or self.board.getProp(self.players[player_num].player_pos).prop_type == Prop_Type.SCHOOL or self.board.getProp(self.players[player_num].player_pos).prop_type == Prop_Type.STATION: #If property actually has a rent attrubite(s)
            if self.board.getProp(self.players[player_num].player_pos).prop_owner != -1 and self.board.getProp(self.players[player_num].player_pos).prop_owner != self.cur_player_num: #If the property is not unowned (i.e. owned) and not owned by current player
                if self.board.getProp(self.players[player_num].player_pos).prop_type == Prop_Type.NORMAL: #Normal Property
                    ret_rent = self.board.getProp(self.players[player_num].player_pos).getRent()
                    if self.board.wholeGroupOwned(self.board.getProp(self.players[player_num].player_pos).prop_owner, self.players[player_num].player_pos) and self.board.getProp(self.players[player_num].player_pos).C_Houses == 0:
                        ret_rent = ret_rent * 2
                elif self.board.getProp(self.players[player_num].player_pos).prop_type == Prop_Type.SCHOOL: #School (dependent on ownership of other schools)
                    ret_rent = self.board.getProp(self.players[player_num].player_pos).getRent(self.board, self.board.getProp(self.players[player_num].player_pos).prop_owner)
                elif self.board.getProp(self.players[player_num].player_pos).prop_type == Prop_Type.STATION: #Station (depedent on ownership of the other station and the roll of the dice)
                    ret_rent = self.board.getProp(self.players[player_num].player_pos).getRent(self.board, self.board.getProp(self.players[player_num].player_pos).prop_owner, self.getDiceTotal())
        if self.board.getProp(self.players[player_num].player_pos).prop_type == Prop_Type.PAYMENT: #Property that cannot be owned by incurs a charge when landed upon (taxes, etc.)
            ret_rent = self.board.getProp(self.players[player_num].player_pos).surcharge
        return ret_rent

    def sendCurPlayerToBog(self):
        self.players[self.getCurPlayerNum()].player_pos = self.board.bogside_pos #Move the player
        self.players[self.getCurPlayerNum()].player_x = self.players[0].calcPieceX(self.board.bogside_pos, self.board.board_sf)
        self.players[self.getCurPlayerNum()].player_y = self.players[0].calcPieceY(self.board.bogside_pos, self.board.board_sf)
        self.players[self.getCurPlayerNum()].enterJail()

    #Apply the effects of a certain card
    def applyCardEffects(self, player_num, card_effects):
        if card_effects[0] != -1: #Player collects money
            self.players[player_num].addMoney(card_effects[0])
        if card_effects[1] != -1: #Player pays money
            self.players[player_num].spendMoney(card_effects[1])
        if card_effects[2] != -1: #Player gets money from each other player
            pay_counter = 0 #No of players who have individually paid
            for counter in range(6):
                if counter != self.cur_player_num: #Player cannot pay themselves
                    try:
                        self.getPlayer(counter).spendMoney(card_effects[2])
                        pay_counter += 1
                    except IndexError: #If index does not exist in the game's Players array, no more players are left that can pay, thus the break
                        break
            self.players[player_num].addMoney(pay_counter * card_effects[2]) #Credit the player as many lots of money as players who paid it
        if card_effects[3] != -1: #Miss a number of turns
            self.players[player_num].setMissTurns(card_effects[3])
        if card_effects[4] != -1: #Move a number of spaces
            self.players[player_num].movePlayer(card_effects[4], self.board)
            self.players[player_num].player_x = self.players[player_num].calcPieceX(self.players[player_num].player_pos, self.board.board_sf)
            self.players[player_num].player_y = self.players[player_num].calcPieceY(self.players[player_num].player_pos, self.board.board_sf)

            #Determine rent if applicable
            self.controller.turn_rent = self.determineRent()

            if self.controller.turn_rent != 0:
                self.players[player_num].spendMoney(self.controller.turn_rent) #Decrease the player's money and credit the owner of the property that amount
                if self.board.getProp(self.players[player_num].player_pos).prop_type != Prop_Type.PAYMENT:
                    self.getPlayer(self.board.getProp(self.players[player_num].player_pos).prop_owner).addMoney(self.controller.turn_rent)
        if card_effects[5] != -1: #Move to a certain spot (and collect money if passing Job Centre)
            orig_pos = self.players[player_num].player_pos
            self.players[player_num].player_pos = card_effects[5]
            self.players[player_num].player_x = self.players[player_num].calcPieceX(self.players[player_num].player_pos, self.board.board_sf)
            self.players[player_num].player_y = self.players[player_num].calcPieceY(self.players[player_num].player_pos, self.board.board_sf)
            if self.players[player_num].player_pos < orig_pos: #Means player must have 'passed' the Job Centre
                self.players[player_num].addMoney(self.board.JC_Money)

            #Determine rent if applicable
            self.controller.turn_rent = self.determineRent()

            if self.controller.turn_rent != 0:
                self.players[player_num].spendMoney(self.controller.turn_rent) #Decrease the player's money and credit the owner of the property that amount
                if self.board.getProp(self.players[player_num].player_pos).prop_type != Prop_Type.PAYMENT:
                    self.getPlayer(self.board.getProp(self.players[player_num].player_pos).prop_owner).addMoney(self.controller.turn_rent)
        if card_effects[6] != -1: #Move to a certain spot (but do not collect money if passing Job Centre)
            self.players[player_num].player_pos = card_effects[6]
            self.players[player_num].player_x = self.players[player_num].calcPieceX(self.players[player_num].player_pos, self.board.board_sf)
            self.players[player_num].player_y = self.players[player_num].calcPieceY(self.players[player_num].player_pos, self.board.board_sf)

            #Determine rent if applicable
            self.controller.turn_rent = self.determineRent()

            if self.controller.turn_rent != 0:
                self.players[player_num].spendMoney(self.controller.turn_rent) #Decrease the player's money and credit the owner of the property that amount
                if self.board.getProp(self.players[player_num].player_pos).prop_type != Prop_Type.PAYMENT:
                    self.getPlayer(self.board.getProp(self.players[player_num].player_pos).prop_owner).addMoney(self.controller.turn_rent)
        if card_effects[7] != -1: #Go to Bogside
            self.sendCurPlayerToBog()
        if card_effects[8] != -1: #Collect a Map out of Bogside
            self.players[player_num].giveBogMap()
        if card_effects[9] != -1: #Pay a certain amount of money for each Council House and Tower Block
            to_pay = 0
            for counter in range(self.board.max_pos+1):
                if self.board.getProp(counter).prop_type == Prop_Type.NORMAL: #Only NORMAL properties acutually possess these upgrades
                    if self.board.getProp(counter).prop_owner == self.cur_player_num: #The current property is owned by this player
                        to_pay += card_effects[9] * (self.board.getProp(counter).C_Houses + self.board.getProp(counter).T_Blocks) #Sum the number of CH and TB
            self.players[player_num].spendMoney(to_pay)
        if card_effects[10] != -1: #Next dice roll's value is decreased
            self.players[player_num].setRollMod(card_effects[10])
        if card_effects[11] != -1: #Pay a certain amount of money for each Council House only
            to_pay = 0
            for counter in range(self.board.max_pos+1):
                if self.board.getProp(counter).prop_type == Prop_Type.NORMAL: #Only NORMAL properties acutually possess these upgrades
                    if self.board.getProp(counter).prop_owner == self.cur_player_num: #The current property is owned by this player
                        to_pay += card_effects[11] * self.board.getProp(counter).C_Houses #Sum the number of CH
            self.players[player_num].spendMoney(to_pay)
        if card_effects[12] != -1: #Pay a certain amount of money for each Tower Block only
            to_pay = 0
            for counter in range(self.board.max_pos+1):
                if self.board.getProp(counter).prop_type == Prop_Type.NORMAL: #Only NORMAL properties acutually possess these upgrades
                    if self.board.getProp(counter).prop_owner == self.cur_player_num: #The current property is owned by this player
                        to_pay += card_effects[12] * self.board.getProp(counter).T_Blocks #Sum the number of TB
            self.players[player_num].spendMoney(to_pay)
        
    #Determine how much money a player could obtain from selling/mortgaging all of their properties and upgrades
    def getObtainMon(self, player_num):
        ret_val = 0

        for counter in range(self.board.max_pos + 1):
            if self.board.getProp(counter).prop_type == Prop_Type.NORMAL:
                if self.board.getProp(counter).prop_owner == player_num:
                    ret_val += int(self.board.getProp(counter).CH_cost * self.board.getProp(counter).C_Houses / 2)
                    ret_val += int(self.board.getProp(counter).TB_cost * self.board.getProp(counter).T_Blocks / 2)
                    if board.getProp(counter).mortgage_status == False:
                        ret_val += board.getProp(counter).mortgage_val

            if self.board.getProp(counter).prop_type == Prop_Type.SCHOOL or self.board.getProp(counter).prop_type == Prop_Type.STATION:
                if self.board.getProp(counter).prop_owner == player_num and self.board.getProp(counter).mortgage_status == False:
                        ret_val += self.board.getProp(counter).mortgage_val
        return ret_val
    
    #Return an integer representing the number of ownable properties on the board that are actually owned by the current player
    def countPropsOwned(self, player_num):
        prop_count = 0
        for counter in range(self.board.max_pos + 1): #Loop through entire board
            if self.board.getProp(counter).prop_type == Prop_Type.NORMAL or self.board.getProp(counter).prop_type == Prop_Type.SCHOOL or self.board.getProp(counter).prop_type == Prop_Type.STATION:
                if self.board.getProp(counter).prop_owner == player_num: #If ownable and owner then increment counter
                    prop_count += 1
        return prop_count

    #Create an array containing the board positions of the properties owned by the current player.
    #Used in Property Details screen
    #Assumed to be for current player
    def setupBoardPoses(self):
        player_num = self.cur_player_num
        num_owned = self.countPropsOwned(player_num)
        ret_arr = list([0] * num_owned) #Initialise integer array
        pos_counter = 0
        for counter in range(self.board.max_pos + 1): #Loop through entire board
            if self.board.getProp(counter).prop_type == Prop_Type.NORMAL:
                if self.board.getProp(counter).prop_owner == player_num:
                    ret_arr[pos_counter] = counter #Set next empty array element to this property's position on the board
                    pos_counter += 1

        #SCHOOL and STATION properties are displayed after all NORMAL ones, as it gives the screen a better aesthetic as a whole
        for counter in range(self.board.max_pos + 1): #Loop through entire board
            if self.board.getProp(counter).prop_type == Prop_Type.SCHOOL or self.board.getProp(counter).prop_type == Prop_Type.STATION:
                if self.board.getProp(counter).prop_owner == player_num:
                    ret_arr[pos_counter] = counter
                    pos_counter += 1
        return ret_arr

    #Determine how much a certain player has spent on all of their properties, upgrades etc.
    def getAssetsVal(self, player_num):
        ret_val = 0

        for counter in range(self.board.max_pos + 1):
            if self.board.getProp(counter).prop_type == Prop_Type.NORMAL:
                if self.board.getProp(counter).prop_owner == player_num:
                    ret_val += self.board.getProp(counter).cost
                    ret_val += (self.board.getProp(counter).CH_cost * self.board.getProp(counter).C_Houses)
                    ret_val += (self.board.getProp(counter).TB_cost * self.board.getProp(counter).T_Blocks)

            if self.board.getProp(counter).prop_type == Prop_Type.SCHOOL or self.board.getProp(counter).prop_type == Prop_Type.STATION:
                if self.board.getProp(counter).prop_owner == player_num:
                    ret_val += self.board.getProp(counter).cost
        return ret_val

    def resetCurPlayerProperties(self):
        for counter in range(self.board.max_pos):
            if self.board.getProp(counter).prop_type == Prop_Type.NORMAL:
                if self.board.getProp(counter).prop_owner == self.cur_player_num:
                    self.board.getProp(counter).prop_owner = -1
                    self.board.getProp(counter).mortgage_status = False
                    self.board.getProp(counter).C_Houses = 0
                    self.board.getProp(counter).T_Blocks = 0
            if self.board.getProp(counter).prop_type == Prop_Type.SCHOOL or mainGame.board.getProp(counter).prop_type == Prop_Type.STATION:
                if self.board.getProp(counter).prop_owner == self.cur_player_num:
                    self.board.getProp(counter).prop_owner = -1
                    self.board.getProp(counter).mortgage_status = False

    # Since all access to this class will be via the Pyro4 interface,
    # objects cannot be returned, so all access to the methods of the subclasses must be defined here.
    #--------------------Board Access--------------------
    def boardBuyCHGroup(self, player_num, prop_num):
        self.board.buyCHGroup(player_num, prop_num)
    
    def boardBuyTBGroup(self, player_num, prop_num):
        self.board.buTBGroup(player_num, prop_num)

    def boardSellCHGroup(self, player_num, prop_num):
        self.board.sellCHGroup(player_num, prop_num)

    def boardSellTBGroup(self, player_num, prop_num):
        self.board.sellTBGroup(player_num, prop_num)
    
    def boardWholeGroupOwned(self, player_num, prop_num):
        return self.board.wholeGroupOwned(player_num, prop_num)
    
    def boardGetMaxPos(self):
        return self.board.max_pos

    def boardGetBogsidePos(self):
        return self.board.bogside_pos

    def boardGetJCMoney(self):
        return self.board.JC_Money
    
    def boardCountGroupSize(self, player_num, prop_num):
        return self.board.countGroupSize(player_num, prop_num)

    #--------------------Card_Deck Access--------------------
    def shufflePLCards(self):
        self.board.PL_Deck.shuffleCards()
    
    def getNextPLCardNum(self):
        return self.board.PL_Deck.getNextCardNum()
    
    def shuffleCCCards(self):
        self.board.CC_Deck.shuffleCards()
    
    def getNextCCCardNum(self):
        return self.board.CC_Deck.getNextCardNum()

    #--------------------Controller Access--------------------
    def getPlayer_rolled(self):
        return self.controller.player_rolled
    
    def getCard_used(self):
        return self.controller.card_used

    def getMay_buy(self):
        return self.controller.may_buy
    
    def getTurn_rent(self):
        return self.controller.turn_rent

    def getCur_card_num(self):
        return self.controller.cur_card_num

    def getCur_card_deck(self):
        return self.controller.cur_card_deck

    def getCur_doubles(self):
        return self.controller.cur_doubles

    def getRoll_num2(self):
        return self.controller.roll_num1

    def getRoll_num2(self):
        return self.controller.roll_num2

    def getCard_effs(self):
        return self.controller.card_effs

    def getCard_texts(self):
        return self.controller.card_texts
    
    def setPlayer_rolled(self, new_val):
        self.controller.player_rolled = new_val

    def setMay_buy(self, new_val):
        self.controller.may_buy = new_val

    def setTurn_rent(self, new_val):
        self.controller.turn_rent = new_val

    def setCur_doubles(self, new_val):
        self.controller.cur_doubles = new_val

    def setCur_card_num(self, new_val):
        self.controller.cur_card_num = new_val

    def setCur_card_deck(self, new_val):
        self.controller.cur_card_deck = new_val

    def setCard_used(self, new_val):
        self.controller.card_used = new_val
    
    #--------------------Die Access--------------------
    def getDieScore(self, num):
        return self.dice[num].cur_score

    def getDiceTotal(self): #Sum score on both dice
        return self.dice[0].cur_score + self.dice[1].cur_score
    
    def rollDice(self):
        self.dice[0].roll()
        self.dice[1].roll()

    #--------------------Player Access--------------------
    def playerSpendMoney(self, amount, player_num):
        self.players[player_num].player_money = self.player_money - amount

    def playerAddMoney(self, amount, player_num):
        self.players[player_num].player_money = self.player_money + amount

    def playerDeactivate(self, player_num):
        self.players[player_num].player_active = False

    def playerEnterJail(self, player_num):
        self.players[player_num].player_inJail = True

    def playerLeaveJail(self, player_num):
        self.players[player_num].player_inJail = False
    
    def movePlayer(self, movePos, player_num):
        self.players[player_num].movePlayer(movePos, self.board)

    def playerSetMissTurns(self, num, player_num):
        self.players[player_num].player_turnsToMiss = num

    def playerSetRollMod(self, newMod, player_num):
        self.players[player_num].player_nextRollMod = newMod

    def playerGiveBogMap(self, player_num):
        self.players[player_num].player_hasBogMap = True

    def playerUseBogMap(self, player_num):
        self.players[player_num].player_hasBogMap = False
    
    def playerGetX(self, player_num):
        return self.players[player_num].player_x

    def playerGetY(self, player_num):
        return self.players[player_num].player_y
    
    def playerGetPos(self, player_num):
        return self.players[player_num].player_pos
    
    def playerGetPieceNum(self, player_num):
        return self.players[player_num].player_piece_num
    
    def playerGetName(self, player_num):
        return self.players[player_num].player_name
    
    def playerGetMoney(self, player_num):
        return self.players[player_num].player_money

    def playerGetInJail(self, player_num):
        return self.players[player_num].player_inJail
    
    def playerGetActive(self, player_num):
        return self.players[player_num].player_active
    
    def playerGetNextRollMod(self, player_num):
        return self.players[player_num].player_nextRollMod
    
    def playerGetTurnsToMiss(self, player_num):
        return self.players[player_num].player_turnsToMiss
    
    def playerGetHasBogMap(self, player_num):
        return self.players[player_num].player_hasBogMap

    #--------------------Property Access--------------------
    def propertyGetRent(self, prop_num):
        return self.board.properties[prop_num].getRent()
    
    def propertyGetMortVal(self, prop_num):
        return self.board.properties[prop_num].mortgage_val

    def propertyGetCH(self, prop_num):
        return self.board.properties[prop_num].C_Houses

    def propertyGetTB(self, prop_num):
        return self.board.properties[prop_num].T_Blocks

    def propertyGetCHCost(self, prop_num):
        return self.board.properties[prop_num].CH_Cost

    def propertyGetTBCost(self, prop_num):
        return self.board.properties[prop_num].TB_Cost

    def propertyGetOwner(self, prop_num):
        return self.board.properties[prop_num].prop_owner

    def propertyGetMortStat(self, prop_num):
        return self.board.properties[prop_num].mortgage_status
    
    def propertySetMortStat(self, prop_num, new_stat):
        self.board.properties[prop_num].mortgage_status = new_stat

    def propertyGetCharge(self, prop_num):
        return self.board.properties[prop_num].getCharge()
    
    def propertyGetTitle(self, prop_num):
        return self.board.properties[prop_num].prop_title

    def propertyGetType(self, prop_num):
        return self.board.properties[prop_num].prop_type
    
    def propertyGetCost(self, prop_num):
        return self.board.properties[prop_num].cost

    def buyProperty(self, prop_num, new_owner):
        self.board.properties[prop_num].buyProperty(new_owner)

    #--------------------Lobby Access--------------------
    def getLobby(self):
        return self.lobby.getLobby()

    def getConns(self):
        return self.lobby.getConns()

    def getUsedPieces(self):
        return self.lobby.getUsedPieces()

    def connect(self, c_ip, c_name):
        self.lobby.connect(c_ip, c_name)
    
    def disconnect(self, c_ip):
        self.lobby.disconnect(c_ip)
    
    def setPiece(self, c_ip, c_piece):
        self.lobby.setPiece(c_ip, c_piece)
    
    def readyUp(self, c_ip):
        self.lobby.readyUp(c_ip)
    
    def readyToStart(self, c_ip):
        self.lobby.readyToStart(c_ip)
    
    def allReadyUp(self):
        return self.lobby.allReadyUp()
    
    def allReadyToStart(self):
        return self.lobby.allReadyToStart()