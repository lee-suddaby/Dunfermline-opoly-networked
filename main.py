import pygame #Used for the creation of the GUI
import random #Generating pseudo-random numbers for dice rolls
import numpy as np #For creation and use of proper arrays as python's default structures are unacceptable
from pygame.locals import * #Another part of the pygame module - contains various constants used by pygame itself
from copy import copy #Used when swapping and copy objects in arrays (e.g. the 2D array quicksort algorithm)
import getpass #Used for getting the user's username, needed for choosing the directory of save files
from datetime import datetime #Getting the current date and time as understood by humans (rather than UNIX time)
import os #Used for creating directories

from textbox import TextBox #TextBox class found on GitHub
from msgbox import MessageBox #MessageBox class is used for (surprisingly enough) displaying message boxes containing text to the user
from anigif import AnimatedGif
from cls import *

#------------------------------Loading Screen functions------------------------------ 
#Determine how many lines are in a text file
#Used when loading the tips file so the number of tips need not be counted
def getFileLines(filePath):
    with open(filePath) as fh:
        #enumerate is a python-specific function used to loop through all lines in the file and keep an incremental counter automatically, similar to a count occurrences algorithm, except here there is no condition to the counting
        #Slightly simply than manually incrementing a separate counter variable and keeping doing so until the end of the file is reached
        for i, l in enumerate(fh,1):
            pass
    return i

#Load tips from text file and populate an array with them
def getTipsFromFile(filePath, fileLines): #num is the number of tips in the file
    tip_arr = np.array([None] * fileLines) #Array to store the Strings that contain the tips. None means no specific length for the string
    fh = open("data/Tips.txt", "r")
    for counter in range(fileLines):
        tip_arr[counter] = fh.readline()
        tip_arr[counter] = tip_arr[counter].strip() #strip() method removes quotation marks
    return tip_arr

#Randomly select another tip to display, with the only condition being that it is different from that currently shown
def getNewTip(old_tip, tip_arr):
    noOfTips = len(tip_arr)
    new_tip = old_tip
    while new_tip == old_tip: #Loop as long as new and old tip are identical; the same tip will hence never be shown twice simultaneouly
         new_tip = tip_arr[random.randint(0,noOfTips-1)]
    return new_tip

#------------------------------New Game Screen Code------------------------------
def countNames(boxes): #Counts how many of the available 6 boxes have had something entered into them
    counter = 0
    for t_box in boxes:
        if len(t_box.getContents()) > 0:
            counter += 1
    return counter

def lengthsValid(boxes): #Checks that none of the names entered have more than 12 characters
    for t_box in boxes:
        if len(t_box.getContents()) > 12: #Maximum allowed length of a username is 12 characters
            return False
    return True

def namesDuplicate(boxes):
    #Cycles through all pairings of username boxes to check for duplication
    for outer in range(5,-1,-1): #Iterates from 5 to 0
        for inner in range(outer): #Iterates up to outer-1
            #Checks a box is being compared with itself and that both actually have a name in them
            if inner != outer and len(boxes[outer].getContents()) > 0 and len(boxes[inner].getContents()) > 0:
                #Username comparison not case-sensitive as allowing both LEE and Lee could lead to confusion
                if boxes[outer].getContents().lower() == boxes[inner].getContents().lower():
                    return True
    return False

def containsComma(boxes):
    for t_box in boxes:
        if "," in t_box.getContents():
            return True
    return False

def namesValid(boxes):
    #Must be at least 2 names entered (as game cannot be played with fewer than 2 players
    #No duplicate names and usernames 12 characters or less as they will not be able to be displayed in an aesthetically pleasing way on screen later otherwise
    if namesDuplicate(boxes) or lengthsValid(boxes) == False or countNames(boxes) < 2 or containsComma(boxes):
        return False
    else:
        return True

def createPlayers(p_icons, boxes, board_dim): #Create Player objects using the names entered into text boxes and the corresponding icons
    new_players = np.array([None] * countNames(boxes))
    p_counter = 0 #Stores which element in the new_players array is next to be instantiated
    for b_counter in range(6):
        if len(boxes[b_counter].getContents()) > 0: #Name must have been entered for a player to come into existence
            p_piece = Player_Piece(getPieceX(0, board_dim/768), getPieceY(0, board_dim/768), pygame.transform.smoothscale(p_icons[b_counter], [32, 32]), b_counter) #Create piece separately
            new_players[p_counter] = Player(1500, p_piece, 0, boxes[b_counter].getContents()) #Now create player. 1500 is the money and 0 is the initial board position
            p_counter += 1
    return new_players

def getCardEffects(card_texts_path_eff): #Loads text file describing the effects of the Pot Luck and Council Chest cards, e.g. "Pay £*", where the * will be replaced with a number later
    texts_num = getFileLines(card_texts_path_eff)
    card_effects = np.array([None] * texts_num) #None used so length of string is not limited
    fh = open(card_texts_path_eff, "r")
    for effects_counter in range(texts_num):
        card_effects[effects_counter] = fh.readline().strip()
    fh.close()
    return card_effects

#Create the decks of Pot Luck and Council Chest cards, based off of data and images loading in from external files
def createDeck(deck_name, card_base_path, card_texts_path, card_data_path, deck_size):
    deck_cards = np.array([None] * deck_size) #Array of blank objects; will become array of individual Card objects
    card_effects = getCardEffects(card_texts_path)
    card_img = None #Blank object, later to become loaded-in pygame images
    text_line = ""

    fh = open(card_data_path, "r")
    for counter in range(deck_size): #Iterate up to deck_size-1
        card_img = pygame.transform.smoothscale(pygame.image.load(card_base_path + str(counter + 1) + ".png"), [330, 200]) #Images are named "Pot Luck 1.png", for example. N.B. Numbering starts at one, hence the +1
        text_line = fh.readline()
        data_array = np.array(text_line.split(",")) #Values are comma-separated in the external file
        for d_count in range(len(data_array)): #Convert each of the elements in the array from String (as they will be coming from an external file) to numbers
            data_array[d_count] = int(data_array[d_count])
        
        deck_cards[counter] = Card(deck_name, card_img, card_effects, data_array)
    fh.close()

    ret_deck = Card_Deck(deck_cards)
    ret_deck.shuffleCards() #Randomly arrange the array of cards such that they will not be the same during every game
    return ret_deck

#Creates an array of properties using data from a data file at the start of the game
def LoadProperties(file_path):
    property_arr = np.array([None]*40) #Partition numpy array with 40 elements
    fh = open(file_path, "r") #Opens the sequential file for reading
    for counter in range(40): #40 properties
        propType = int(fh.read(2)[:1]) #Reads in the first two characters in a line (one number and a separating comma) and then takes the first character. This leaves propType being an integer determining which type of property the line is for
        line_text = fh.readline() #Read in the rest of the line, where all data is for a single property
        prop_values = np.array(line_text.split(",")) #Transforms the string into an array where each comma-separated item is an indivual element

        if propType == 0: #Most common property type
            property_arr[counter] = Normal_Property(prop_values, CreateTitleDeed(prop_values), CreateMortDeed(prop_values[0], int(prop_values[10])*1.2))
        elif propType == 1: #School (requires crest image for title deed)
            property_arr[counter] = School_Property(prop_values, pygame.image.load("img/Deeds/" + str(prop_values[0]) + ".png"), CreateMortDeed(prop_values[0], int(prop_values[6])*1.2))
        elif propType == 2: #Stations (requires crest image for title deed)
            property_arr[counter] = Station_Property(prop_values, pygame.image.load("img/Deeds/" + str(prop_values[0]) + ".png"), CreateMortDeed(prop_values[0], int(prop_values[4])*1.2))
        elif propType == 3: #Pot Luck card spot
            property_arr[counter] = Property(prop_values[0].strip(), Prop_Type.POT_LUCK)
        elif propType == 4: #Council Chest card spot
            property_arr[counter] = Property(prop_values[0].strip(), Prop_Type.COUNCIL_CHEST)
        elif propType == 5: #Lost In Bogside spot
            property_arr[counter] = Property(prop_values[0].strip(), Prop_Type.LOST_IN_BOGSIDE)
        elif propType == 6: #Go To Bogside space
            property_arr[counter] = Go_To_Bogside(prop_values[0].strip(), prop_values[1])
        elif propType == 7: #Property that incurs a charge when landed upon
            property_arr[counter] = Charge_Property(prop_values[0].strip(), prop_values[1])
        elif propType == 8: #Job Centre where the player collects money when passing it
            property_arr[counter] = Property(prop_values[0].strip(), Prop_Type.JOB_CENTRE)
        elif propType == 9: #Disabled Parking - Does nothing as of yet (and it probably never will)
            property_arr[counter] = Property(prop_values[0].strip(), Prop_Type.DISABLED_PARKING)
    fh.close()
    return property_arr #Array of 40 Property (or subclass) objects

#Create the Board object that will become part of the Game class later
def createBoard(data_file_path, props_arr, Pot_Luck, Council_Chest, image_path, image_dim):
    fh = open(data_file_path, "r")
    bog_pos = int(fh.readline()) #Board position of what would be the jail
    centre_mon = int(fh.readline()) #Money obtained upon passing the Job Centre
    fh.close()

    board_img = pygame.image.load(image_path) #Load and resize board image
    board_img = pygame.transform.smoothscale(board_img, [image_dim, image_dim])
    scale_f = image_dim/768 #Used in piece positioning - formulae were created for a 768x768 board

    ret_board = Board(props_arr, bog_pos, centre_mon, Pot_Luck, Council_Chest, board_img, scale_f)
    return ret_board

#Create the final Game object - this is the main point of the New Game screen
def createGame(game_players, game_board, game_save, dice_imgs_base_paths):
    dice_imgs = np.array([None] * 6)
    for d_count in range(6):
        dice_imgs[d_count] = pygame.image.load(dice_imgs_base_paths + str(d_count+1) + ".png") #+1 as dice images are stored with numbers 1 to 6 in the file
    dice_arr = np.array([None] * 2)
    dice_arr[0] = Die(dice_imgs)
    dice_arr[1] = Die(dice_imgs)

    ret_game = Game(game_players, dice_arr, game_board, game_save)
    return ret_game

#Create an array of game players based on data loaded in from a file
def LoadPlayers(load_arr):
    new_players = np.array([None] * int(load_arr[0][1])) #load_arr[0][1] stores the number of players
    for counter in range(len(new_players)):
        p_piece = Player_Piece(getPieceX(int(load_arr[counter+1][2]), 600/768), getPieceY(int(load_arr[counter+1][2]), 600/768), pygame.transform.smoothscale(pygame.image.load('img/Pieces/' + str(int(load_arr[counter+1][3])+1) + '.png'), [32, 32]), int(load_arr[counter+1][3])) #Create piece separately. load-arr[counter+1][3] stores a number from 0-5 relating to which of the token images is used (1.png - 6.png)
        new_players[counter] = Player(int(load_arr[counter+1][1]), p_piece, int(load_arr[counter+1][2]), load_arr[counter+1][0], bool(int(load_arr[counter+1][8])), bool(int(load_arr[counter+1][7]))) #Second element (not [counter+1]) is related to the order in which the data was saved, which can be seen in Game.saveGame method
        new_players[counter].hasBogMap = bool(int(load_arr[counter+1][4])) #Relevant element of this array
        new_players[counter].nextRollMod = int(load_arr[counter+1][5]) #Final player attributes being restored
        new_players[counter].turnsToMiss = int(load_arr[counter+1][6])
    return new_players

#Render a title deed for a property (that can be mortgaged) for when it is actually mortgaged
#Only shows the name, buy-back cost and a mnessage explaining that the property needs to be rebought for it to collect rent again
def CreateMortDeed(deed_name, deed_cost):
    deed_screen = pygame.Surface((250,400))
    deed_screen.fill((255,255,255)) #Filled white

    deed_font_name = pygame.font.SysFont('Arial', 24, True) #Font for property name (bold)
    deed_font_desc = pygame.font.SysFont('Arial', 18) #Font for descriptive text that tells the user that the property will not collect rent while still mortgaged
    deed_font_back = pygame.font.SysFont('Arial', 28) #Font for displaying the cost to unmortgage/buy-back the property

    pygame.draw.rect(deed_screen, (0,0,0), pygame.Rect(0,0,250,400), 2) #Title deed outline

    prop_text = deed_font_name.render(deed_name, True, (0,0,0)) #Name of property (in bold) at the top of the deed
    f_width, f_height = deed_font_name.size(deed_name) #Used repeatedly so that text can be centred, using the equation (xpos = (deed_width-text_width)/2)
    deed_screen.blit(prop_text, [(250-f_width)/2, 80])

    desc_text_1 = deed_font_desc.render('This property is currently mortgaged.', True, (0,0,0)) #First line of the deed description
    f_width, f_height = deed_font_desc.size('This property is currently mortgaged.')
    deed_screen.blit(desc_text_1, [(250-f_width)/2, 140])

    desc_text_2 = deed_font_desc.render('It will not collect rent until bought back.', True, (0,0,0)) #Second line of the deed description
    f_width, f_height = deed_font_desc.size('It will not collect rent until bought back.')
    deed_screen.blit(desc_text_2, [(250-f_width)/2, 158])

    buy_back_text = deed_font_back.render('Buy-Back Cost £' + str(int(deed_cost)), True, (0,0,0)) #Text displaying how much it costs to unmortgage the property
    f_width, f_height = deed_font_back.size('Buy-Back Cost £' + str(int(deed_cost)))
    deed_screen.blit(buy_back_text, [(250-f_width)/2, 275])
    
    return deed_screen

#Render a title deed for a typical property based on its rents, cost,
#etc Returns a pygame Surface containing shapes and text resembling a
#title deed
def CreateTitleDeed(deed_vals):
    deed_screen = pygame.Surface((225,400))
    deed_screen.fill((255,255,255)) #Filled white

    deed_col = pygame.Color(int(deed_vals[11]), int(deed_vals[12]), int(deed_vals[13]), 0) #Create colour to be used in header from the 3 separate RGB values
    #Create fonts for title deed
    deed_font_main = pygame.font.SysFont('Arial', 18) #Font for most text
    deed_font_name = pygame.font.SysFont('Arial', 20, True) #Bold font holding the name of the property
    deed_font_bottom = pygame.font.SysFont('Arial', 14) #Font for displaying the info at the bottom of the property about rent doubling if all properties in the gropup are owned

    pygame.draw.rect(deed_screen, (0,0,0), pygame.Rect(0,0,225,400), 2) #Title deed outline
    pygame.draw.rect(deed_screen, deed_col, pygame.Rect(5, 5, 215, 100)) #Coloured rectangle containing the words 'Title Deed' and property name
    
    prop_text = deed_font_name.render(deed_vals[0], True, (255,255,255)) #Name of property (in bold) at bottom of above coloured rectangle
    f_width, f_height = deed_font_name.size(deed_vals[0]) #Used repeatedly so that text can be centred, using the equation (xpos = (deed_width-text_width)/2)
    deed_screen.blit(prop_text, [(225-f_width)/2, 95 - f_height])

    title_text = deed_font_main.render('Title Deed', True, (255,255,255)) #Words 'Title Deed' at the top of the aforementioned coloured rectangle
    f_width, f_height = deed_font_main.size('Title Deed')
    deed_screen.blit(title_text, [(225-f_width)/2, 5])

    cost_text = deed_font_main.render('Cost £' + str(deed_vals[1]), True, (0,0,0)) #The cost to buy the property from the bank
    f_width, f_height = deed_font_main.size('Cost £' + str(deed_vals[1]))
    deed_screen.blit(cost_text, [(225-f_width)/2, 105])
    
    rent_text = deed_font_main.render('Rent £' + str(deed_vals[2]), True, (0,0,0)) #Rent on the unimproved property
    f_width, f_height = deed_font_main.size('Rent £' + str(deed_vals[2]))
    deed_screen.blit(rent_text, [(225-f_width)/2, 123])

    ch_text1 = deed_font_main.render('With 1 Council House', True, (0,0,0)) #Basic text providing a textual explanation for the 4 rent values with Council Houses
    deed_screen.blit(ch_text1, [15, 153])
    ch_text2 = deed_font_main.render('With 2 Council Houses', True, (0,0,0))
    deed_screen.blit(ch_text2, [15, 173])
    ch_text3 = deed_font_main.render('With 3 Council Houses', True, (0,0,0))
    deed_screen.blit(ch_text3, [15, 193])
    ch_text4 = deed_font_main.render('With 4 Council Houses', True, (0,0,0))
    deed_screen.blit(ch_text4, [15, 213])

    ch_rent1 = deed_font_main.render('£' + str(deed_vals[3]), True, (0,0,0)) #Rent values for 1, 2, 3 and 4 council houses
    f_width, f_height = deed_font_main.size('£' + str(deed_vals[3]))
    deed_screen.blit(ch_rent1, [210-f_width, 153])
    ch_rent2 = deed_font_main.render('£' + str(deed_vals[4]), True, (0,0,0))
    f_width, f_height = deed_font_main.size('£' + str(deed_vals[4]))
    deed_screen.blit(ch_rent2, [210-f_width, 173])
    ch_rent3 = deed_font_main.render('£' + str(deed_vals[5]), True, (0,0,0))
    f_width, f_height = deed_font_main.size('£' + str(deed_vals[5]))
    deed_screen.blit(ch_rent3, [210-f_width, 193])
    ch_rent4 = deed_font_main.render('£' + str(deed_vals[6]), True, (0,0,0))
    f_width, f_height = deed_font_main.size('£' + str(deed_vals[6]))
    deed_screen.blit(ch_rent4, [210-f_width, 213])

    tb_rent = deed_font_main.render('With Tower Block £' + str(deed_vals[7]), True, (0,0,0)) #Rent with a tower block on the property
    f_width, f_height = deed_font_main.size('With Tower Block £' + str(deed_vals[7]))
    deed_screen.blit(tb_rent, [(225-f_width)/2, 233])

    mortgage_val = deed_font_main.render('Mortgage Value £' + str(deed_vals[10]), True, (0,0,0)) #Mortgage value on property
    f_width, f_height = deed_font_main.size('Mortgage Value £' + str(deed_vals[10]))
    deed_screen.blit(mortgage_val, [(225-f_width)/2, 260])

    ch_cost = deed_font_main.render('Council Houses cost £' + str(deed_vals[8]) + ' each', True, (0,0,0)) #Cost of a council house for this property
    f_width, f_height = deed_font_main.size('Council Houses cost £' + str(deed_vals[8]) + ' each')
    deed_screen.blit(ch_cost, [(225-f_width)/2, 280])

    tb_cost = deed_font_main.render('Tower Block costs £' + str(deed_vals[9]) + ',', True, (0,0,0)) #Cost of a tower block for this property
    f_width, f_height = deed_font_main.size('Tower Block costs £' + str(deed_vals[9]) + ',')
    deed_screen.blit(tb_cost, [(225-f_width)/2, 300])
    tb_info = deed_font_main.render('plus 4 Council Houses', True, (0,0,0))
    f_width, f_height = deed_font_main.size('plus 4 Council Houses')
    deed_screen.blit(tb_info, [(225-f_width)/2, 318])

    bottom_note1 = deed_font_bottom.render('If a player owns all properties in this', True, (0,0,0)) #Note at bottom of the title deed about rent doubling 
    f_width, f_height = deed_font_bottom.size('If a player owns all properties in this') #if all properties in a group are owned and unimproved
    deed_screen.blit(bottom_note1, [(225-f_width)/2, 350])
    bottom_note2 = deed_font_bottom.render('group, rent is doubled on properties with', True, (0,0,0))
    f_width, f_height = deed_font_bottom.size('group, rent is doubled on properties with')
    deed_screen.blit(bottom_note2, [(225-f_width)/2, 364])
    bottom_note3 = deed_font_bottom.render('no Council Houses or Tower Blocks', True, (0,0,0))
    f_width, f_height = deed_font_bottom.size('no Council Houses or Tower Blocks')
    deed_screen.blit(bottom_note3, [(225-f_width)/2, 378])

    return deed_screen

#------------------------------Main Game Functions------------------------------
#Create the thumbnails showing all the properties on the board
#highlighting all the ones owned by a certain player
#Graphic returned is always the same size; its size on screen must be chosen when it is actually displayed if it needs to be different
def CreateThumbs(board, player):
    colour_on = pygame.Color(0,0,0)
    t_width = 45
    t_height = 70
    colour_counter = 0
    groups_done = 0
    specials = 0 #schools and stations
    
    thumbnails = pygame.Surface((450,200)) #Create new surface on which to blit title deed thumbnails as they are generated
    thumbnails.fill((255,255,255)) #Screen starts white
    
    for counter in range(board.max_pos+1): #For each property
        if board.getProp(counter).getType() == Prop_Type.NORMAL: #Most common property, so one with a 'normal' title deed
            if board.getProp(counter).getGroupCol() != colour_on: #If we have reached a new group, reset the counter and note the new current group colour
                colour_on = board.getProp(counter).getGroupCol() #Set new current group colour
                colour_counter = 0 #Reset colour
                groups_done = groups_done + 1 #New group, so that's another one completed
            else: #Still on the same property group
                colour_counter = colour_counter + 1 #Increment counter

            #Create thumbnail using separate function
            #Second argument is a condition which evaluates to a boolean, hence becoming the value of this actual parameter passed into the CreatePropThumb function
            cur_thumb = CreatePropThumb(board.getProp(counter).getGroupCol(), board.getProp(counter).getOwner() == player) 
            #Complicated mathematical calculations to determine the exact position of the current thumbnail.
            #If in the same group, there is 5 pixels of movement to the right for each property, and vertical movement is one third of each thumbnails's height
            thumbnails.blit(cur_thumb, [(groups_done-1)*(t_width+int(t_width/5)) + colour_counter*int(t_width/5), colour_counter*int(t_height/3)])
        elif board.getProp(counter).getType() == Prop_Type.SCHOOL or board.getProp(counter).getType() == Prop_Type.STATION: #School and station properties
            specials = specials + 1
            cur_thumb = CreateThumbImg("img/Thumbs/" + board.getProp(counter).getTitle() + ".png", board.getProp(counter).getOwner() == player)
            thumbnails.blit(cur_thumb, [(specials-1)*t_width + (specials-1)*int(t_width/5), 120]) #All these thumbnails are displayed in one horizontal line; therefore the same y-coordinate each time
    return thumbnails #pygame.Surface object that can be displayed on the screen as an image
            #441 x117

#Create an individual thumbnail to become a part of the method above (CreateThumbs)
#Only applicable for 'normal' properties; those that have images used the similar CreateThumbImg method
def CreatePropThumb(colour, bought):
    thumb = pygame.Surface((45,70))
    thumb.fill((255,255,255))

    outline = pygame.Rect(0,0,45,70)
    pygame.draw.rect(thumb, (0,0,0), outline, 1) #Thin black border outlining the entire title deed thumbnail

    top_rect = pygame.Rect(1,1,43,20)
    pygame.draw.rect(thumb, colour, top_rect) #Top of the title deed, where colour represents the property group

    #Black lines representing what would be text on the full size title deeds
    for counter in range(4):
        pygame.draw.line(thumb, (0,0,0), [5, counter*10 + 28], [40, counter*10 + 28], 4)

    if not bought: #Semi-transparent white overlay that makes the thumbnail look greyed out, compared to the fully coloured thumbnail if the property is owned
        overlay = pygame.Surface((45,70), pygame.SRCALPHA) #pygame.SRCALPHA allows the creation of a semi-transparent image
        overlay.fill((255,255,255,196)) #White overlay created here. 196 is the 'alpha' value, where 0 is full transparency and 255 is fully opaque
        thumb.blit(overlay, (0,0))
    return thumb #returns a pygame.Surface (i.e. pygame image)

#Creates thumbnail for school and station type properties, since they have an image (insiginia) on their title deeds
def CreateThumbImg(img_path, bought):
    thumb = pygame.Surface((45,70))
    thumb.fill((255,255,255))

    outline = pygame.Rect(0,0,45,70)
    pygame.draw.rect(thumb, (0,0,0), outline, 1) #Black border for the deed

    deed_img = pygame.transform.smoothscale(pygame.image.load(img_path), [35, 40]) #Load deed image (school crest or station logo)
    thumb.blit(deed_img, [5,3]) #Display so this it is horizontally centred

    pygame.draw.line(thumb, (0,0,0), [5, 50], [40, 50], 4) #Create black lines as would appear on the fully sized deed
    pygame.draw.line(thumb, (0,0,0), [5, 60], [40, 60], 4)

    if not bought: #Semi-transparent white overlay that makes the thumbnail look greyed out, compared to the fully coloured thumbnail if the property is owned
        overlay = pygame.Surface((45,70), pygame.SRCALPHA)
        overlay.fill((255,255,255,196))
        thumb.blit(overlay, (0,0))
    return thumb

def displayPropThumbs(thumbs, x_pos, y_pos):
    screen.blit(thumbs, [x_pos, y_pos])

#Determine the x and y coordinates of a player's token based on which property of the board it is occupying
#The calculations were based off of testing that used linear regression to find an 'optimal' relationship between board position and coordinate positions
#Scale factor (sf) is used so board size can easily be changed, as calculations were created with a 768x768 board
def getPieceX(pos, sf):
    p_x = 0
    if 10 <= pos <= 20:
        p_x = 10
    elif pos == 0 or pos >= 30:
        p_x = 710
    elif pos < 10:
        p_x = 666 - 61*pos
    elif 20 < pos < 30:
        p_x = 61*pos - 1168
    return p_x * sf

def getPieceY(pos, sf):
    p_y = 0
    if 0 <= pos <= 10:
        p_y = 710
    elif 20 <= pos <= 30:
        p_y = 10
    elif 10 < pos < 20:
        p_y = 1281 - 61*pos
    elif 30 < pos:
        p_y = 61*pos - 1767
    return p_y * sf

#Fill the screen white and show the game board
def displayScreenAndBoard(board_img):
    screen.fill((255,255,255))
    screen.blit(board_img, [0,0])

#Show text displaying the number of the current player
def displayWhoseTurn(font, player):
    turn_text = font.render(player.player_name, True, (0,0,0))
    screen.blit(turn_text, (650, 10))

#Render text showing how much money the current player has on screen
def displayPlayerMoney(font, player_money):
    turn_text = font.render('£' + str(player_money), True, (0,0,0))
    f_width, f_height = font.size('£' + str(player_money))
    screen.blit(turn_text, (1000-f_width, 10))

#Display the token (i.e. the thing that moves around the board for the current player)
def displayPlayerToken(player):
    screen.blit(pygame.transform.smoothscale(player.player_piece.piece_img, [50,50]), [600, 0])

#Display the graphic for, and number owned, of the available Council House and Tower Block upgrades
def displayUpgrades(ch_img, tb_img, prop, font):
    screen.blit(ch_img, [400, 615]) #Display Council House graphic on screen
    screen.blit(tb_img, [570, 610]) #Display Tower Block graphic on screen
    ch_num = font.render(str(prop.getCH()), True, (0,0,0)) #Generate and display the numbers of each of the upgardes horizontally next to the graphics
    tb_num = font.render(str(prop.getTB()), True, (0,0,0))
    screen.blit(ch_num, [360, 630])
    screen.blit(tb_num, [530, 630])

#For an owned property, display the player (Player 1, etc.) that actually is the owner
def displayOwner(font, prop_owner):
    own_text = font.render('Owned By: ' + prop_owner.player_name, True, (0,0,0)) #+1 because first player is indexed zero, and humans don't start counting at zero.
    f_width, f_height = font.size('Owned By: ' + prop_owner.player_name)
    screen.blit(own_text, ((400-f_width)/2 + 600, 630))

#Display a properties rent from the point of view of it having been paid
def displayPaidRent(font, rent):
    rent_text = font.render('You Paid £' + str(rent), True, (0,0,0))
    f_width, f_height = font.size('You Paid £' + str(rent))
    screen.blit(rent_text, ((400-f_width)/2 + 600, 660))
    
#Display a properties rent from its owner's perspecitve
def displayRent(font, rent):
    rent_text = font.render('Current Rent - £' + str(rent), True, (0,0,0))
    f_width, f_height = font.size('Current Rent - £' + str(rent))
    screen.blit(rent_text, ((400-f_width)/2 + 600, 660))

#Display a Council Chest or Pot Luck card (only called if applicable)
def displayCard(display_card):
    screen.blit(display_card.card_img, [635, 270])

#Render the texts describing the effects of the cards. Also returns the array of numerical values
def renderCardTexts(font, card):
    effs = card.card_nums #Obtain the numerical values for the effects
    texts = card.card_effects #Obtain the textual descriptors of the effects
    eff_count = 0 #Count how many effects are used in this card
    for counter in range(len(effs)):
        if int(effs[counter]) != -1: #-1 means not used
            eff_count += 1

    ret_texts = np.array([None] * eff_count) #Create final array, to later contain pygame text objects
    t_count = 0
    for counter in range(len(effs)):
        if int(effs[counter]) != -1:
            ret_texts[t_count] = font.render(texts[counter].replace("*", str(effs[counter])), True, (0,0,0)) #* is used where in the texts where it should be replaced with the number
            t_count += 1
    return effs, ret_texts

#Display the two images representing the scores on the two rolled dice
def displayDiceScore(img_1, img_2):
    if img_1 != None and img_2 != None: #If there are actually images to display
        screen.blit(img_1, [185, 690])
        screen.blit(img_2, [255, 690])

#Generic function for creating a rectangle that can be used as a button, of a certain size, in a certain position and colour, and with a certain textual caption
def displayButton(x, y, w, h, but_col, font, caption, txt_col):
    rect = pygame.Rect(x,y,w,h)
    pygame.draw.rect(screen, but_col, rect)

    f_width, f_height = font.size(caption)
    cap_text = font.render(caption, True, txt_col)
    screen.blit(cap_text, [(w-f_width)/2 + x,(h-f_height)/2 + y]) #Displays the text in the centre of the button - (button_width - text_width)/2

#Generic function similar to displayButton(), but where it uses a pygame.Rect object (which I also use for mouse click collision detection) in drawing the button
def displayButtonRect(rect, but_col, font, caption, txt_col):
    pygame.draw.rect(screen, but_col, rect)

    f_width, f_height = font.size(caption)
    cap_text = font.render(caption, True, txt_col)
    screen.blit(cap_text, [(rect.width-f_width)/2 + rect.left,(rect.height-f_height)/2 + rect.top]) #Displays the text in the centre of the button - (button_width - text_width)/2

#Display the tokens of every player on the relevant property on the board
def displayPieces(gameObj):
    for counter in range(6):
        try:
            if gameObj.getPlayer(counter).player_active: #Only show the pieces of active players
                screen.blit(gameObj.getPlayer(counter).player_piece.piece_img, [gameObj.getPlayer(counter).player_piece.piece_x, gameObj.getPlayer(counter).player_piece.piece_y])
                if counter == gameObj.cur_player: #Draw red circle around the current player's token to highlight it to them
                    pygame.draw.circle(screen, (255,0,0), [int(gameObj.getPlayer(counter).player_piece.piece_x + 16), int(gameObj.getPlayer(counter).player_piece.piece_y + 16)], 20, 5)
        except IndexError: #If index does not exist in the game's Players array, no more players are left to show, thus the break
            break

#Checks if the group to which a certain property belongs 
def wholeGroupOwned(board, player_num, prop_num):
    if board.getProp(prop_num).getType() != Prop_Type.NORMAL:
        return False
    find_col = board.getProp(prop_num).getGroupCol() #Colour of the group whose coalescence of ownership is being investigated
    for counter in range(board.max_pos + 1):
        if board.getProp(counter).getType() == Prop_Type.NORMAL: #Prevents errors as no other types have a Group Colour
            if board.getProp(counter).getGroupCol() == find_col and board.getProp(counter).getOwner() != player_num:
                #This property is the same colour as the one that is being examined, however, the owner is different so this player cannot own the entire group
                return False
    return True

#Counts the number of properties that are a memeber of a certain property's 'colour group'
def countGroupSize(board, player_num, prop_num):
    if board.getProp(prop_num).getType() != Prop_Type.NORMAL: #Only NORMAL properties have a colour group
        return 0
    group_count = 0
    find_col = board.getProp(prop_num).getGroupCol() #Colour of the group which we are concerned with
    for counter in range(board.max_pos + 1):
        if board.getProp(counter).getType() == Prop_Type.NORMAL: #Prevents errors as no other types have a Group Colour
            if board.getProp(counter).getGroupCol() == find_col and board.getProp(counter).getOwner() == player_num:
                group_count += 1
    return group_count

#Add 1 Council House upgrade to every property in a certain group
def buyCHGroup(board, player_num, prop_num):
    if board.getProp(prop_num).getType() == Prop_Type.NORMAL:
        find_col = board.getProp(prop_num).getGroupCol() #Colour of the group which we are concerned with
        for counter in range(board.max_pos + 1):
            if board.getProp(counter).getType() == Prop_Type.NORMAL: #Prevents errors as no other types have a Group Colour
                if board.getProp(counter).getGroupCol() == find_col and board.getProp(counter).getOwner() == player_num:
                    board.getProp(counter).buyCH()

#Add 1 Tower Block upgrade to every property in a certain group
def buyTBGroup(board, player_num, prop_num):
    if board.getProp(prop_num).getType() == Prop_Type.NORMAL:
        find_col = board.getProp(prop_num).getGroupCol() #Colour of the group which we are concerned with
        for counter in range(board.max_pos + 1):
            if board.getProp(counter).getType() == Prop_Type.NORMAL: #Prevents errors as no other types have a Group Colour
                if board.getProp(counter).getGroupCol() == find_col and board.getProp(counter).getOwner() == player_num:
                    board.getProp(counter).buyTB()

#Remove 1 Council House upgrade from every property in a certain group
def sellCHGroup(board, player_num, prop_num):
    if board.getProp(prop_num).getType() == Prop_Type.NORMAL:
        find_col = board.getProp(prop_num).getGroupCol() #Colour of the group which we are concerned with
        for counter in range(board.max_pos + 1):
            if board.getProp(counter).getType() == Prop_Type.NORMAL: #Prevents errors as no other types have a Group Colour
                if board.getProp(counter).getGroupCol() == find_col and board.getProp(counter).getOwner() == player_num:
                    board.getProp(counter).sellCH()

#Remove 1 Council House upgrade from every property in a certain group
def sellTBGroup(board, player_num, prop_num):
    if board.getProp(prop_num).getType() == Prop_Type.NORMAL:
        find_col = board.getProp(prop_num).getGroupCol() #Colour of the group which we are concerned with
        for counter in range(board.max_pos + 1):
            if board.getProp(counter).getType() == Prop_Type.NORMAL: #Prevents errors as no other types have a Group Colour
                if board.getProp(counter).getGroupCol() == find_col and board.getProp(counter).getOwner() == player_num:
                    board.getProp(counter).sellTB()
                    
def determineRent(gameObj):
    ret_rent = 0
    if gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getType() == Prop_Type.NORMAL or gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getType() == Prop_Type.SCHOOL or gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getType() == Prop_Type.STATION: #If property actually has a rent attrubite(s)
        if gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getOwner() != -1 and gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getOwner() != gameObj.cur_player: #If the property is not unowned (i.e. owned) and not owned by current player
            if gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getType() == Prop_Type.NORMAL: #Normal Property
                ret_rent = gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getRent()
                if wholeGroupOwned(gameObj.board, gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getOwner(), gameObj.getCurPlayer().player_pos) and gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getCH() == 0:
                    ret_rent = ret_rent * 2
            elif gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getType() == Prop_Type.SCHOOL: #School (dependent on ownership of other schools)
                ret_rent = gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getRent(gameObj.board, gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getOwner())
            elif gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getType() == Prop_Type.STATION: #Station (depedent on ownership of the other station and the roll of the dice)
                ret_rent = gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getRent(gameObj.board, gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getOwner(), gameObj.getDiceTotal())
    if gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getType() == Prop_Type.PAYMENT: #Property that cannot be owned by incurs a charge when landed upon (taxes, etc.)
        ret_rent = gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getCharge()
    return ret_rent

def sendCurPlayerToBog(gameObj):
    gameObj.getCurPlayer().player_pos = gameObj.board.bogside_pos #Move the player
    gameObj.getCurPlayer().player_piece.piece_x = getPieceX(gameObj.getCurPlayer().player_pos, gameObj.board.board_sf) #Update piece co-ordinates as well
    gameObj.getCurPlayer().player_piece.piece_y = getPieceY(gameObj.getCurPlayer().player_pos, gameObj.board.board_sf)
    gameObj.getCurPlayer().enterJail()

#Apply the effects of a certain card
def applyCardEffects(gameObj, card_effects):
    if card_effects[0] != -1: #Player collects money
        gameObj.getCurPlayer().addMoney(card_effects[0])
    if card_effects[1] != -1: #Player pays money
        gameObj.getCurPlayer().spendMoney(card_effects[1])
    if card_effects[2] != -1: #Player gets money from each other player
        pay_counter = 0 #No of players who have individually paid
        for counter in range(6):
            if counter != gameObj.cur_player: #Player cannot pay themselves
                try:
                    gameObj.getPlayer(counter).spendMoney(card_effects[2])
                    pay_counter += 1
                except IndexError: #If index does not exist in the game's Players array, no more players are left that can pay, thus the break
                    break
        gameObj.getCurPlayer().addMoney(pay_counter * card_effects[2]) #Credit the player as many lots of money as players who paid it
    if card_effects[3] != -1: #Miss a number of turns
        gameObj.getCurPlayer().setMissTurns(card_effects[3])
    if card_effects[4] != -1: #Move a number of spaces
        gameObj.getCurPlayer().movePlayer(card_effects[4], gameObj.board)
        gameObj.getCurPlayer().player_piece.piece_x = getPieceX(gameObj.getCurPlayer().player_pos, gameObj.board.board_sf) #Update piece co-ordinates as well
        gameObj.getCurPlayer().player_piece.piece_y = getPieceY(gameObj.getCurPlayer().player_pos, gameObj.board.board_sf)

        #Determine rent if applicable
        gameObj.controller.turn_rent = determineRent(gameObj)

        if gameObj.controller.turn_rent != 0:
            gameObj.getCurPlayer().spendMoney(gameObj.controller.turn_rent) #Decrease the player's money and credit the owner of the property that amount
            if gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getType() != Prop_Type.PAYMENT:
                gameObj.getPlayer(gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getOwner()).addMoney(gameObj.controller.turn_rent)
    if card_effects[5] != -1: #Move to a certain spot (and collect money if passing Job Centre)
        orig_pos = gameObj.getCurPlayer().player_pos
        gameObj.getCurPlayer().player_pos = card_effects[5]
        gameObj.getCurPlayer().player_piece.piece_x = getPieceX(gameObj.getCurPlayer().player_pos, gameObj.board.board_sf) #Update piece co-ordinates as well
        gameObj.getCurPlayer().player_piece.piece_y = getPieceY(gameObj.getCurPlayer().player_pos, gameObj.board.board_sf)
        if gameObj.getCurPlayer().player_pos < orig_pos: #Means player must have 'passed' the Job Centre
            gameObj.getCurPlayer().addMoney(gameObj.board.JC_Money)

        #Determine rent if applicable
        gameObj.controller.turn_rent = determineRent(gameObj)

        if gameObj.controller.turn_rent != 0:
            gameObj.getCurPlayer().spendMoney(gameObj.controller.turn_rent) #Decrease the player's money and credit the owner of the property that amount
            if gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getType() != Prop_Type.PAYMENT:
                gameObj.getPlayer(gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getOwner()).addMoney(gameObj.controller.turn_rent)
    if card_effects[6] != -1: #Move to a certain spot (but do not collect money if passing Job Centre)
        gameObj.getCurPlayer().player_pos = card_effects[6]
        gameObj.getCurPlayer().player_piece.piece_x = getPieceX(gameObj.getCurPlayer().player_pos, gameObj.board.board_sf) #Update piece co-ordinates as well
        gameObj.getCurPlayer().player_piece.piece_y = getPieceY(gameObj.getCurPlayer().player_pos, gameObj.board.board_sf)

        #Determine rent if applicable
        gameObj.controller.turn_rent = determineRent(gameObj)

        if gameObj.controller.turn_rent != 0:
            gameObj.getCurPlayer().spendMoney(gameObj.controller.turn_rent) #Decrease the player's money and credit the owner of the property that amount
            if gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getType() != Prop_Type.PAYMENT:
                gameObj.getPlayer(gameObj.board.getProp(gameObj.getCurPlayer().player_pos).getOwner()).addMoney(gameObj.controller.turn_rent)
    if card_effects[7] != -1: #Go to Bogside
        sendCurPlayerToBog(gameObj)
    if card_effects[8] != -1: #Collect a Map out of Bogside
        gameObj.getCurPlayer().giveBogMap()
    if card_effects[9] != -1: #Pay a certain amount of money for each Council House and Tower Block
        to_pay = 0
        for counter in range(gameObj.board.max_pos+1):
            if gameObj.board.getProp(counter).getType() == Prop_Type.NORMAL: #Only NORMAL properties acutually possess these upgrades
                if gameObj.board.getProp(counter).getOwner() == gameObj.cur_player: #The current property is owned by this player
                    to_pay += card_effects[9] * (gameObj.board.getProp(counter).getCH() + gameObj.board.getProp(counter).getTB()) #Sum the number of CH and TB
        gameObj.getCurPlayer().spendMoney(to_pay)
    if card_effects[10] != -1: #Next dice roll's value is decreased
        gameObj.getCurPlayer().setRollMod(card_effects[10])
    if card_effects[11] != -1: #Pay a certain amount of money for each Council House only
        to_pay = 0
        for counter in range(gameObj.board.max_pos+1):
            if gameObj.board.getProp(counter).getType() == Prop_Type.NORMAL: #Only NORMAL properties acutually possess these upgrades
                if gameObj.board.getProp(counter).getOwner() == gameObj.cur_player: #The current property is owned by this player
                    to_pay += card_effects[11] * gameObj.board.getProp(counter).getCH() #Sum the number of CH
        gameObj.getCurPlayer().spendMoney(to_pay)
    if card_effects[12] != -1: #Pay a certain amount of money for each Tower Block only
        to_pay = 0
        for counter in range(gameObj.board.max_pos+1):
            if gameObj.board.getProp(counter).getType() == Prop_Type.NORMAL: #Only NORMAL properties acutually possess these upgrades
                if gameObj.board.getProp(counter).getOwner() == gameObj.cur_player: #The current property is owned by this player
                    to_pay += card_effects[12] * gameObj.board.getProp(counter).getTB() #Sum the number of TB
        gameObj.getCurPlayer().spendMoney(to_pay)
        
#------------------------------Property Details Functions------------------------------
#Return an integer representing the number of ownable properties on the board that are actually owned by the current player
def countPropsOwned(board, player_num):
    prop_count = 0
    for counter in range(board.max_pos + 1): #Loop through entire board
        if board.getProp(counter).getType() == Prop_Type.NORMAL or board.getProp(counter).getType() == Prop_Type.SCHOOL or board.getProp(counter).getType() == Prop_Type.STATION:
            if board.getProp(counter).getOwner() == player_num: #If ownable and owner then increment counter
                prop_count += 1
    return prop_count

#Create an array containing the board positions of the properties owned by the current player
def setupBoardPoses(board, player_num, num_owned):
    ret_arr = np.array([0] * num_owned) #Initialise integer array
    pos_counter = 0
    for counter in range(board.max_pos + 1): #Loop through entire board
        if board.getProp(counter).getType() == Prop_Type.NORMAL:
            if board.getProp(counter).getOwner() == player_num:
                ret_arr[pos_counter] = counter #Set next empty array element to this property's position on the board
                pos_counter += 1

    #SCHOOL and STATION properties are displayed after all NORMAL ones, as it gives the screen a better aesthetic as a whole
    for counter in range(board.max_pos + 1): #Loop through entire board
        if board.getProp(counter).getType() == Prop_Type.SCHOOL or board.getProp(counter).getType() == Prop_Type.STATION:
            if board.getProp(counter).getOwner() == player_num:
                ret_arr[pos_counter] = counter
                pos_counter += 1
    return ret_arr

#------------------------------Leaderboards Functions------------------------------
#Determine how much a certain player has spent on all of their properties, upgrades etc.
def getAssetsVal(board, player_num):
    ret_val = 0

    for counter in range(board.max_pos + 1):
        if board.getProp(counter).getType() == Prop_Type.NORMAL:
            if board.getProp(counter).getOwner() == player_num:
                ret_val += board.getProp(counter).getCost()
                ret_val += (board.getProp(counter).getCHCost() * board.getProp(counter).getCH())
                ret_val += (board.getProp(counter).getTBCost() * board.getProp(counter).getTB())

        if board.getProp(counter).getType() == Prop_Type.SCHOOL or board.getProp(counter).getType() == Prop_Type.STATION:
            if board.getProp(counter).getOwner() == player_num:
                ret_val += board.getProp(counter).getCost()
    return ret_val

#Determine how much money a player could obtain from selling/mortgaging all of their properties and upgrades
def getObtainMon(board, player_num):
    ret_val = 0

    for counter in range(board.max_pos + 1):
        if board.getProp(counter).getType() == Prop_Type.NORMAL:
            if board.getProp(counter).getOwner() == player_num:
                ret_val += int(board.getProp(counter).getCHCost() * board.getProp(counter).getCH() / 2)
                ret_val += int(board.getProp(counter).getTBCost() * board.getProp(counter).getTB() / 2)
                if board.getProp(counter).getMortgageStatus() == False:
                    ret_val += board.getProp(counter).getMortgageVal()

        if board.getProp(counter).getType() == Prop_Type.SCHOOL:
            if board.getProp(counter).getOwner() == player_num and board.getProp(counter).getMortgageStatus == False:
                    ret_val += board.getProp(counter).getMortgageVal()
    return ret_val

#Get number of players in the game
def countPlayers(gameObj):
    ret_num = 0
    for counter in range(6):
        try:
            if gameObj.getPlayer(counter).player_active:
                ret_num += 1
        except IndexError:
            break
    return ret_num

#Create a 2D array to store the leaderboards data
#One column for player numbers, one for total money, one for assets value (includes money) and one for obtainable money (also includes the player's money)
def setup2DArray(gameObj):
    no_of_players = countPlayers(gameObj)
    ret_2D = np.zeros((no_of_players,4), int)
    arr_count = 0
    for counter in range(len(gameObj.players)):
        if gameObj.getPlayer(counter).player_active: 
            ret_2D[arr_count][0] = counter
            ret_2D[arr_count][1] = gameObj.getPlayer(counter).player_money
            ret_2D[arr_count][2] = getAssetsVal(gameObj.board, counter)
            ret_2D[arr_count][3] = gameObj.getPlayer(counter).player_money + getObtainMon(gameObj.board, counter)
            arr_count += 1
    return ret_2D

#Used for sorting the player data on a certain column in the 2D array (one column for each comparable attribute)
#asc is a boolean storing whether the array is being sorted ascending or descending (True for ascending, False for descending)
def quickSort(sort_arr, first, last, sort_col, asc):
    low = first
    high = last
    midValue = sort_arr[int((first+last)/2)][sort_col] #Middle item in the array

    while low <= high:
        if asc:
            while sort_arr[low][sort_col] < midValue:
                low += 1
            while sort_arr[high][sort_col] > midValue:
                high -= 1
        else:
            while sort_arr[low][sort_col] > midValue:
                low += 1
            while sort_arr[high][sort_col] < midValue:
                high -= 1

        if low <= high:
            sort_arr[low], sort_arr[high] = copy(sort_arr[high]), copy(sort_arr[low]) #Swap the two rows
            #copy is used here as otherwise, python does not actually copy the data, rather just pointers which mean the array ends up unsorted and with duplicated rows, despite a perfectly working algorithm
            low += 1
            high -= 1

    if first < high:
        sort_arr = quickSort(sort_arr, first, high, sort_col, asc) #Recursively call function, with differing partitions on the array

    if low < last:
        sort_arr = quickSort(sort_arr, low, last, sort_col, asc) #Recursively call function, with differing partitions on the array

    return sort_arr #Pass the array back out to where it was called, ending this level of recursion

        
#------------------------------Loading Screen Code------------------------------      
#Initialise pygame
pygame.init()
clock = pygame.time.Clock()

#Count number of tips and populate the array of tips from the external file
tips_num = getFileLines("data/Tips.txt")
tipsArr = getTipsFromFile("data/Tips.txt", tips_num)
tip_use = getNewTip("", tipsArr) #Choose a tip to display first

tip_font = pygame.font.SysFont('Arial', 24) #Font used to display a tip
tip_text = tip_font.render(tip_use, True, (255,255,255)) #Actually render the tip text in the recently-created font
t_width, t_height = tip_font.size(tip_use) #Get width and height for centring the text

#Displays the text "Top Tip:", essentially showing what the tips are
tip_text2 = tip_font.render("Top Tip:", True, (255,255,255))
t_width2, t_height2 = tip_font.size("Top Tip:")

but_font = pygame.font.SysFont('Arial', 48) #Font for the play button
but_text = but_font.render("Play", True, (0,0,0)) #Create text for play button
b_width, b_height = but_font.size("Play")

#Create array of 12 strings, containing the paths of each of the frames of the coin animation
imagesCA = np.array([" "*32] * 12)
for counter in range(12):
    imagesCA[counter] = "img/CA/coin_frame_" + str(counter+1) + ".png"

#Set width and height of the pygame screen
height = 360
width = 936

main = pygame.transform.smoothscale(pygame.image.load("img/Title.png"), [width, int(height/2)]) #Dunfermline-opoly title
coin1 = AnimatedGif(int(50*width/468),int(210*height/360),int(64*width/468),int(64*width/468),imagesCA) #Two coin animations at the bottom-left and bottom-right corners of the screen
coin2 = AnimatedGif(int(354*width/468),int(210*height/360),int(64*width/468),int(64*width/468),imagesCA)#Coin animations are animated GIFS created using the AnimatedGif class
Play_but = pygame.Rect((width-200)/2, (850-height)/2, 200, 80) #Rectangle used both for the main part of the play button, and for detecting when the button is clicked
    
screen = pygame.display.set_mode([width,height], pygame.NOFRAME)
screen.fill((0,0,0))

running = True
tip_counter = 0 #Counts how many frames the current tip has been displayed for
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: #If escape key is pressed
                running = False #Game exists completely
                pygame.quit() 
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: #Left mouse button
                mouse_pos = event.pos     
                if Play_but.collidepoint(mouse_pos): #If mouse down and over play button (in other words, if play button clicked)
                    running = False #This screen is finished with; move to next screen

    #Clear screen and display title, and the current frame of each GIF                
    screen.fill((0,0,0))
    screen.blit(main, [0,0])
    screen.blit(coin1.getCurFrame(), [coin1.gif_x,coin1.gif_y])
    screen.blit(coin2.getCurFrame(), [coin2.gif_x,coin2.gif_y])

    if tip_counter > 50: #50 frames = 5 seconds
        #Reset tip counter, randomly choose a new, different tip and render that in the appropriate font
        tip_counter = 0
        tip_use = getNewTip(tip_use, tipsArr)
        tip_text = tip_font.render(tip_use, True, (255,255,255)) #Recreate the string in pygame text so that it can be displayed on screen
        t_width, t_height = tip_font.size(tip_use) #Used for centring the text

    #Display the tip title and the actual tip itself
    screen.blit(tip_text2, [(width-t_width2)/2, (330-t_height2)/2])
    screen.blit(tip_text, [(width-t_width)/2,(380-t_height)/2])

    #Display the Play button
    displayButtonRect(Play_but, (100,100,100), but_font, 'Play', (0,0,0))
    
    tip_counter = tip_counter + 1
    clock.tick(10)
    pygame.display.flip() #Update display


#------------------------------New Game Code------------------------------ 
def NewGame():
    mainGame = None #Create new object that will eventually become a Game object
    pieces = np.array([None] * 6) #Array to store the 6 images for the player icons that will be linked to the textboxes
    for p_counter in range(6):
        pieces[p_counter] = pygame.transform.smoothscale(pygame.image.load("img/Pieces/" + str(p_counter+1) + ".png"), [50, 50]) #Load image into pygame and resize

    box_arr = np.array([None] * 6) #Array of 6 textboxes - one to one correspondence with the elements of the pieces array
    for b_counter in range(6):
        #Indices related to location on screen:
        #0                       1
        #2                       3
        #4                       5
        #Additional kwargs allow for control over additional behaviour/functionality, much of which is never utilised in this game
        box_arr[b_counter] = TextBox((100 + 500*(b_counter%2), 175 + 55*int(b_counter/2), 380, 50), clear_on_enter=False, inactive_on_enter=False, active=False, active_color=pygame.Color("red"))
    save_path_box = TextBox((340, 550, 640, 50), clear_on_enter=False, inactive_on_enter=False, active=False, active_color=pygame.Color("red"))

    now = datetime.now()
    #Save file name is in the form YYYYMMDD_HHMMSS.dfo
    month = '0' + str(now.month)
    day = '0' + str(now.day)
    hour = '0' + str(now.hour)
    minute = '0' + str(now.minute)
    second = '0' + str(now.second)
    save_initial = 'C:/Users/' + getpass.getuser() + '/Dunfermline-opoly/' + str(now.year) + month[-2:] + day[-2:] + '_' + hour[-2:] + minute[-2:] + second[-2:] + '.dfo'
    save_path_box.buffer = list(save_initial)

    create_game_button = pygame.Rect(150,650,300,80) #This lot is used for registering if mouse clicks are on a certain button
    load_game_button = pygame.Rect(600,650,300,80)
    exit_button = pygame.Rect(870,20,120,70)
    info_button = pygame.Rect(935,100,55,55)
    font_48 = pygame.font.SysFont('Arial', 48) #Fonts used for texts
    font_60 = pygame.font.SysFont('Arial', 60)

    msgBox = None
    
    create_but_click = False
    load_but_click = False
    screen_running = True
    while screen_running:
        for event in pygame.event.get():
            if msgBox != None:
                msgBox.handle_input_event(event)
                if msgBox.should_exit == False:
                    break
            if event.type == pygame.QUIT:
                screen_running = False
                gotoScreen = -1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: #Escape key exits the game
                    screen_running = False
                    gotoScreen = -1 #Game will completely exit
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #Left mouse button
                    mouse_pos = event.pos #Position of the cursor when nouse was clicked
                    if exit_button.collidepoint(mouse_pos): #Button used to exit this screen/the entire game
                        screen_running = False
                        gotoScreen = -1
                    if create_game_button.collidepoint(mouse_pos): #Button for creating the game
                        create_but_click = True
                    if load_game_button.collidepoint(mouse_pos):
                        load_but_click = True
                    if info_button.collidepoint(mouse_pos): #Button for finding out what the pieces represent
                         msgBox = MessageBox(screen, 'Bottle: A common and very possibly-alcoholic beverage enjoyed often enjoyed by Dunfermine residents (only those over 18 of course). \n Can: A popular soft drink that definitely does not infringe upon any Intellectual Property Rights. \n Coal: Coal mining was a prosperous (albeit dangerous) industry  for hundreds of years in the Dunfermline and Fife area. \n Crown: Dunfermline is a royal burgh. \n Badly-drawn Sheep: Sheep farming is very common in the Dunfermline area. \n Battleship: Dunfermline is situated near to the Royal Navy dockyard in Rosyth.', 'Token Info')
            for box in box_arr: 
                box.get_event(event) #Function that allows each textbox to register key presses and the like
            save_path_box.get_event(event)
            

        screen.fill((255,255,255)) #Clear the screen
        #Display 3 buttons whose functions should be relatively self-explanatory based on their captions
        displayButtonRect(create_game_button, (100,100,100), font_60, 'Create Game', (0,0,0))
        displayButtonRect(load_game_button, (100,100,100), font_60, 'Load Game', (0,0,0))
        displayButtonRect(exit_button, (100,100,100), font_48, 'Exit', (0,0,0))
        displayButtonRect(info_button, (100,100,100), font_48, '?', (0,0,0))
        
        #Display pure text aspects of the screen
        new_game_title = font_60.render("New Game:", True, (0,0,0))
        screen.blit(new_game_title, [10, 10])

        icon_title = font_48.render("Enter Player Names (max 12 characters)", True, (0,0,0))
        screen.blit(icon_title, [30, 75])

        save_title = font_48.render("Save File Path:", True, (0,0,0))
        screen.blit(save_title, [50, 545])
        
        for box in box_arr:
            box.update() #To do with internal workings - take clicks, key pressed etc. into account
        for box in box_arr:
            box.draw(screen)   #Display the boxes on screen - one of the TextBox classes methods 
        save_path_box.update() #Do the same as above but for the object that is not part of the array
        save_path_box.draw(screen)

        for piece_count in range(6): #Display the 6 pieces on screen to the left of the relevant text box
            screen.blit(pieces[piece_count], [45 + 500*(piece_count%2), 175 + 55*int(piece_count/2)])

        if create_but_click: #If button to create the game itself was clicked
            valid = True #Whether the file part of the process is alright
            if save_path_box.getContents()[-3:].lower() != "dfo": #Must have correct file ending, or invalid
                msgBox = MessageBox(screen, 'Invalid file. Please ensure the entered file has the correct .dfo file ending.', 'File Error')
                valid = False

            if valid:   
                try:
                    os.makedirs(os.path.dirname(save_path_box.getContents()), exist_ok=True)
                    f = open(save_path_box.getContents(), 'w+')
                except: #Any error occurs in creating the directory or file
                    msgBox = MessageBox(screen, 'Invalid save file entered. Please ensure the path entered exists and you have permissions to access it (the file does not have to)', 'Invalid Save File')
                    valid = False

            if valid:
                if namesValid(box_arr): #Validate the player's username
                    players = createPlayers(pieces, box_arr, 600) #Create array of Player objects
                    prop_arr = LoadProperties("data/Property Values.txt") #Create array of Property objects
                    Pot_Luck_Deck = createDeck("Pot Luck", "img/PL/Pot Luck ", "data/Card_Texts.txt", "data/PL Master.txt", 16) #Create Card_Deck object
                    Council_Chest_Deck = createDeck("Council Chest", "img/CC/Council Chest ", "data/Card_Texts.txt", "data/CC Master.txt", 16) #Create Card_Deck object
                    game_board = createBoard("data/Board_Data.txt", prop_arr, Pot_Luck_Deck, Council_Chest_Deck, "img/Board.png", 600) #Create Board object

                    mainGame = createGame(players, game_board, save_path_box.getContents(), "img/Dice/") #Finally create the single, cohesive Game object that is the sole purpose of this screen/part of the game
                    
                    screen_running = False
                    gotoScreen = 1 #1=Main game screen
                else:
                    msgBox = MessageBox(screen, 'The names you entered are invalid. Please ensure all names are 12 characters or less, different (this part is not case-sensitive) and you have entered at least two user names', 'Invalid Usernames')                    

        if load_but_click:
            valid = True
            if save_path_box.getContents()[-3:].lower() != "dfo": #Must have correct file ending, or invalid
                msgBox = MessageBox(screen, 'Invalid file. Please select a different file or create a new game', 'File Error')
                valid = False
                
            try:
                f = open(save_path_box.getContents(), 'r')
            except: #If an error occurs, then also invalid
                msgBox = MessageBox(screen, 'Cannot open file. Please select a different file or create a new game', 'File Error')
                valid = False

            if valid:
                data_arr = []
                for line in f:
                    data_arr.append(line.strip().split(','))
                data_arr = np.array(data_arr)
                
                players = LoadPlayers(data_arr)    
                prop_arr = LoadProperties("data/Property Values.txt") #Create array of Property objects
                Pot_Luck_Deck = createDeck("Pot Luck", "img/PL/Pot Luck ", "data/Card_Texts.txt", "data/PL Master.txt", 16) #Create Card_Deck object
                Council_Chest_Deck = createDeck("Council Chest", "img/CC/Council Chest ", "data/Card_Texts.txt", "data/CC Master.txt", 16) #Create Card_Deck object
                game_board = createBoard("data/Board_Data.txt", prop_arr, Pot_Luck_Deck, Council_Chest_Deck, "img/Board.png", 600) #Create Board object

                for counter in range(int(data_arr[0][1])+1, len(data_arr)):
                    if game_board.getProp(int(data_arr[counter][0])).getType() == Prop_Type.NORMAL:
                        game_board.getProp(int(data_arr[counter][0])).buyProperty(int(data_arr[counter][1]))
                        game_board.getProp(int(data_arr[counter][0])).C_Houses = int(data_arr[counter][2])
                        game_board.getProp(int(data_arr[counter][0])).T_Blocks = int(data_arr[counter][3])
                        game_board.getProp(int(data_arr[counter][0])).setMortgageStatus(bool(int(data_arr[counter][4])))
                    elif game_board.getProp(int(data_arr[counter][0])).getType() == Prop_Type.STATION or game_board.getProp(int(data_arr[counter][0])).getType() == Prop_Type.SCHOOL:
                        game_board.getProp(int(data_arr[counter][0])).buyProperty(int(data_arr[counter][1]))
                        game_board.getProp(int(data_arr[counter][0])).setMortgageStatus(bool(int(data_arr[counter][2])))
                    
                mainGame = createGame(players, game_board, save_path_box.getContents(), "img/Dice/") #Finally create the single, cohesive Game object that is the sole purpose of this screen/part of the game
                mainGame.cur_player = int(data_arr[0][0]) #Positions in array as per the order of saving, which can be seen in the method within the Game class
                mainGame.autosave = bool(int(data_arr[0][2]))
                
                screen_running = False
                gotoScreen = 1 #1=Main game screen            
          
        if msgBox != None:
            msgBox.update()
            if msgBox.should_exit == False:
                msgBox.draw(screen)

        create_but_click = False
        load_but_click = False
        clock.tick(30) #30 fps
        pygame.display.flip() #Refresh screen

    return mainGame, gotoScreen #Pass the Game object and the integer storing where the game will go to next back out to the main game loop


#------------------------------Main Game Code------------------------------         
def MainScreen(mainGame):
    mainGame.prop_thumbs = pygame.transform.smoothscale(CreateThumbs(mainGame.board, mainGame.cur_player), [385,170])

    roll_dice_button = pygame.Rect(180,610,150,70) #Create rectangle for roll dice/end turn button
    buy_prop_button = pygame.Rect(675,690,250,70) #Create rectangle for property buying button (also used for mortgaging and unmortgaging
    pause_button = pygame.Rect(10,610,150,70)
    leaderboard_button = pygame.Rect(10,690,150,70)
    buy_upgrade_button = pygame.Rect(350,700,150,50)
    sell_upgrade_button = pygame.Rect(520,700,150,50)
    details_button = pygame.Rect(900,160,100,50)
    in_jail_button = pygame.Rect(350,610,150,70)

    TB_img = pygame.transform.smoothscale(pygame.image.load("img/Tower Block.png"), [75, 75])
    CH_img = pygame.transform.smoothscale(pygame.image.load("img/Council House.png"), [75, 75])
    
    font_40 = pygame.font.SysFont('Arial', 40) #Font object for button captions
    font_28 = pygame.font.SysFont('Arial', 28) #font object for displaying whose turn it is (among other things)
    font_20 = pygame.font.SysFont('Arial', 20) #Font for the upgrade buttons
    
    #maxpos = 39 #Index of the final property before you get back to the start

    dice_but_click = False #Booleans tracking whether the roll dice, end turn and but property buttons have been clicked yet this turn
    turn_but_click = False
    buy_but_click = False
    mort_but_click = False
    buy_upgrade_but_click = False
    sell_upgrade_but_click = False
    leave_bogside_but_click = False
    use_card_but_click = False

    msgBox = None
    exitOnBoxClose = False
    advanceOnBoxClose = False
    fps = 10 #Used to determine the waiting between updating the game display

    main_screen_running = True
    while main_screen_running:
        for event in pygame.event.get():
            if msgBox != None:
                msgBox.handle_input_event(event)
                if exitOnBoxClose and msgBox.should_exit:
                    main_screen_running = False
                    gotoScreen = -1
                if advanceOnBoxClose and msgBox.should_exit:
                    mainGame.advancePlayer()
                    mainGame.prop_thumbs = pygame.transform.smoothscale(CreateThumbs(mainGame.board, mainGame.cur_player), [385,170]) #Generate thumbnails for new player (here so it is only done when the player changes, not every frame change)
                    advanceOnBoxClose = False
                if msgBox.should_exit == False:
                    break
            if event.type == pygame.QUIT:
                main_screen_running = False
                gotoScreen = -1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: #Escape key exits the game
                    main_screen_running = False
                    gotoScreen = -1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #Left mouse button
                    mouse_pos = event.pos #Position of the cursor when nouse was clicked
                    if buy_prop_button.collidepoint(mouse_pos):
                        if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getOwner() == -1: #Property is unowned
                            buy_but_click = True
                        elif mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getOwner() == mainGame.cur_player: #If owned by current player, it may be mortgaged
                            mort_but_click = True
                    if roll_dice_button.collidepoint(mouse_pos):
                        if mainGame.controller.card_used == False:
                            use_card_but_click = True #Roll dice button was clicked
                        elif mainGame.controller.player_rolled == False:
                            dice_but_click = True #End turn button was clicked
                        else:
                            turn_but_click = True #Button to apply card effects was clicked
                    if in_jail_button.collidepoint(mouse_pos): #Button to pay £50 to get out of bogside was clicked
                        leave_bogside_but_click = True
                    if buy_upgrade_button.collidepoint(mouse_pos):
                        buy_upgrade_but_click = True
                    if sell_upgrade_button.collidepoint(mouse_pos):
                        sell_upgrade_but_click = True
                    if details_button.collidepoint(mouse_pos):
                        main_screen_running = False
                        gotoScreen = 2
                    if leaderboard_button.collidepoint(mouse_pos):
                        main_screen_running = False
                        gotoScreen = 3
                    if pause_button.collidepoint(mouse_pos):
                        main_screen_running = False
                        gotoScreen = 4
                    
        #Clear screen and display main board
        displayScreenAndBoard(mainGame.board.board_img)
        
        if dice_but_click: #If Roll Dice button was clicked
            #Roll dice, move the piece accordingly, and display the dice rolls
            mainGame.getDie(0).roll()
            mainGame.getDie(1).roll()

            dice_total = mainGame.getDiceTotal()
            
            if mainGame.getCurPlayer().player_inJail == False:
                mainGame.getCurPlayer().movePlayer(dice_total, mainGame.board)
            elif mainGame.getDie(0).cur_score == mainGame.getDie(1).cur_score: #Doubles rolled, so player gets out of bogside
                mainGame.getCurPlayer().leaveJail()
                mainGame.getCurPlayer().movePlayer(dice_total, mainGame.board)
            #Player does not move otherwise, as they must be lost in bogside

            #Generate the dice images
            mainGame.controller.roll_img1 = pygame.transform.smoothscale(mainGame.getDie(0).getImg(), [70, 70])
            mainGame.controller.roll_img2 = pygame.transform.smoothscale(mainGame.getDie(1).getImg(), [70, 70])
            
            #Determine piece's place on the board
            mainGame.getCurPlayer().player_piece.piece_x = getPieceX(mainGame.getCurPlayer().player_pos, mainGame.board.board_sf)
            mainGame.getCurPlayer().player_piece.piece_y = getPieceY(mainGame.getCurPlayer().player_pos, mainGame.board.board_sf)

            if mainGame.getDie(0).cur_score != mainGame.getDie(1).cur_score: #If a double has not been rolled (rolling a double gives the player another turn)
                mainGame.controller.player_rolled = True #So player only gets another turn if they rolled doubles
            mainGame.controller.may_buy = True

            if mainGame.getDie(0).cur_score == mainGame.getDie(1).cur_score:
                mainGame.controller.cur_doubles += 1
                
            if mainGame.controller.cur_doubles >= 3: #If player rolls 3 consecutive doubles, they go to Bogside
                sendCurPlayerToBog(mainGame)
                mainGame.controller.player_rolled = True #Will not get to roll again
            
            #Determine rent if applicable
            mainGame.controller.turn_rent = determineRent(mainGame)

            if mainGame.controller.turn_rent != 0:
                mainGame.getCurPlayer().spendMoney(mainGame.controller.turn_rent) #Decrease the player's money and credit the owner of the property that amount
                if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() != Prop_Type.PAYMENT:
                    mainGame.getPlayer(mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getOwner()).addMoney(mainGame.controller.turn_rent)

            #If the current space returns a card
            if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.POT_LUCK:
                mainGame.controller.cur_card = mainGame.board.PL_Deck.getNextCard()
            elif mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.COUNCIL_CHEST:
                mainGame.controller.cur_card = mainGame.board.CC_Deck.getNextCard()

            #If card will have just been returned, render the text that will show its effects
            if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.POT_LUCK or mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.COUNCIL_CHEST: #Card will have been returned
                mainGame.controller.card_effs, mainGame.controller.card_texts = renderCardTexts(font_28, mainGame.controller.cur_card)
                mainGame.controller.card_used = False
                                
            #If the player lands on the 'Go To Bogside' space
            if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.GO_TO_BOGSIDE:
                sendCurPlayerToBog(mainGame)

            
        #Display whose turn it is, how much money this player has, and show their property overview
        displayWhoseTurn(font_28, mainGame.getCurPlayer())
        displayPlayerMoney(font_28, mainGame.getCurPlayer().player_money)
        displayPlayerToken(mainGame.getCurPlayer())
        displayPropThumbs(mainGame.prop_thumbs, 610, 50)
        displayDiceScore(mainGame.controller.roll_img1, mainGame.controller.roll_img2)
        
        #Display buttons for viewing the pause menu, property details and leaderboards
        displayButtonRect(leaderboard_button, (100, 100, 100), font_28, 'Leaderboards', (0, 0, 0))
        displayButtonRect(pause_button, (100, 100, 100), font_40, 'Pause', (0, 0, 0))
        displayButtonRect(details_button, (100, 100, 100), font_28, 'Details', (0, 0, 0))
        
        #Show each of the player's pieces at its requisite position on the board
        displayPieces(mainGame)

        #Show the Roll Dice/End Turn button, and the appropriate caption
        if mainGame.controller.card_used == False:
            displayButtonRect(roll_dice_button, (100, 100, 100), font_40, 'Use Card', (0, 0, 0))
        elif mainGame.controller.player_rolled == False:
            displayButtonRect(roll_dice_button, (100, 100, 100), font_40, 'Roll Dice', (0, 0, 0))
        else:
            displayButtonRect(roll_dice_button, (100, 100, 100), font_40, 'End Turn', (0, 0, 0))

        if mainGame.getCurPlayer().player_inJail and mainGame.getCurPlayer().player_hasBogMap: #If player is lost in bogside, but they have the equivelant of a "Get out of Jail Free" card
            displayButtonRect(in_jail_button, (100, 100, 100), font_28, 'Use Map', (0, 0, 0))
        elif mainGame.getCurPlayer().player_inJail: #Don't have card
            displayButtonRect(in_jail_button, (100, 100, 100), font_28, 'Buy Map (£50)', (0, 0, 0))

        #Display title deed for property currently on
        if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.NORMAL or mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.SCHOOL or mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.STATION: #If property actually will have a title deed to display
            title_deed = pygame.transform.smoothscale(mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getTitleDeed(), [270,400])
            screen.blit(title_deed, [665, 230])

            if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.NORMAL:
                #Normal properties are the only ones that can have Council Houses and Tower Blocks on them
                displayUpgrades(CH_img, TB_img, mainGame.board.getProp(mainGame.getCurPlayer().player_pos), font_40)

                if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getOwner() == mainGame.cur_player:
                    if wholeGroupOwned(mainGame.board, mainGame.cur_player, mainGame.getCurPlayer().player_pos): #May only be bought if the property is owned by the current player and the entire colour group is owned
                    
                        if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getCH() < 4:
                            displayButtonRect(buy_upgrade_button, (100, 100, 100), font_20, 'Buy Council House', (0, 0, 0))
                        elif mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getTB() == 0:
                            displayButtonRect(buy_upgrade_button, (100, 100, 100), font_20, 'Buy Tower Block', (0, 0, 0))

                        if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getTB() > 0:
                            displayButtonRect(sell_upgrade_button, (100, 100, 100), font_20, 'Sell Tower Block', (0, 0, 0))
                        elif mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getCH() > 0:
                            displayButtonRect(sell_upgrade_button, (100, 100, 100), font_20, 'Sell Council House', (0, 0, 0))

                    #Display relevant button for mortgaging or unmortgaging a property
                    if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getMortgageStatus(): #Property is mortgaged
                        displayButtonRect(buy_prop_button, (100, 100, 100), font_28, 'Unmortgage Property', (0, 0, 0))
                    else:
                        displayButtonRect(buy_prop_button, (100, 100, 100), font_28, 'Mortgage Property', (0, 0, 0))

            if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getOwner() == -1 and mainGame.controller.may_buy:
                #Give player the opportunity to buy property (since it is available and they have began their turn by rolling the dice)
                displayButtonRect(buy_prop_button, (100, 100, 100), font_40, 'Buy Property', (0, 0, 0))
            elif mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getOwner() != -1:
                #Property is owned by a player so display information pertaining to the owning of said property by this aforementioned player
                displayOwner(font_28, mainGame.getPlayer(mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getOwner()))
        else:
            if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() != Prop_Type.LOST_IN_BOGSIDE: #Will work perfectly normally for all properties but the Lost In Bogside square
                tit_str = mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getTitle()
            elif mainGame.getCurPlayer().player_inJail: #If Player is actually 'in jail'
                tit_str = "Lost In Bogside"
            else:
                tit_str = "On The Paths" #In the same space but can move freely (i.e. 'not in jail')
                
            tit_text = font_40.render(tit_str, True, (0,0,0)) #Render the property name as it does not have a title deed that can do so
            t_width, t_height = font_40.size(tit_str)
            screen.blit(tit_text, [(400-t_width)/2 + 600, 220])

        if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.NORMAL or mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.SCHOOL or mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.STATION or mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.PAYMENT: #If incurs a charge
            try:
                if mainGame.controller.turn_rent != 0: #If rent has actually been charged then the player is told they themselves have paid whatever amount
                    displayPaidRent(font_28, mainGame.controller.turn_rent)
                elif mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getOwner() == mainGame.cur_player and mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.NORMAL: #If property is owned by the current player and NORMAL (since other properties depend on those owned and dice rolls
                    if wholeGroupOwned(mainGame.board, mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getOwner(), mainGame.getCurPlayer().player_pos) and mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getCH() == 0:
                        displayRent(font_28, mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getRent()*2)
                    else:
                        displayRent(font_28, mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getRent())
            except AttributeError: #Prevents errors as PAYMENT property has no owner but changes variable turn_rent
                pass
            
        if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.POT_LUCK or mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.COUNCIL_CHEST:
            if mainGame.controller.cur_card != None: #If player was already on one of these places when their turn begins, cur_card and card_texts will be None object; this condition prevents an error when the following code thinks that it is
                displayCard(mainGame.controller.cur_card)
                t_count = 0
                for cur_text in mainGame.controller.card_texts:
                    w, h = cur_text.get_size()
                    screen.blit(cur_text, [(400-w)/2 + 600, 480 + t_count*25])
                    t_count += 1
        
        if turn_but_click: #End Turn button
            #If player could sell some things to avoid going bankrupt
            cont = True
            if mainGame.getCurPlayer().player_money < 0 and (getObtainMon(mainGame.board, mainGame.cur_player) + mainGame.getCurPlayer().player_money) >= 0:
                msgBox = MessageBox(screen, 'You need to ensure your money is 0 or above before you can finish your turn. Please sell or mortgage some assets to continue.', 'Not Enough Money')
                cont = False
            elif (getObtainMon(mainGame.board, mainGame.cur_player) + mainGame.getCurPlayer().player_money) < 0: #If it is impossible for a player to not end up in debt, they go bankrupt
                mainGame.getCurPlayer().deactivate() #Remove player from the game
                cont = False
                for counter in range(mainGame.board.max_pos):
                    if mainGame.board.getProp(counter).getType() == Prop_Type.NORMAL:
                        if mainGame.board.getProp(counter).getOwner() == mainGame.cur_player:
                            mainGame.board.getProp(counter).p_owner = -1
                            mainGame.board.getProp(counter).setMortgageStatus(False)
                            mainGame.board.getProp(counter).C_Houses = 0
                            mainGame.board.getProp(counter).T_Blocks = 0
                    if mainGame.board.getProp(counter).getType() == Prop_Type.SCHOOL or mainGame.board.getProp(counter).getType() == Prop_Type.STATION:
                        if mainGame.board.getProp(counter).getOwner() == mainGame.cur_player:
                            mainGame.board.getProp(counter).p_owner = -1
                            mainGame.board.getProp(counter).setMortgageStatus(False)
                        
                msgBox = MessageBox(screen, 'Unfortunately, this utopian capitalist world has ceased to be utopian for you: you have gone bankrupt and are no longer in the game.', 'Game Over')
                advanceOnBoxClose = True
                
            #Next player's turn now (if the previous player has no more to do
            if cont:
                mainGame.advancePlayer()
                mainGame.prop_thumbs = pygame.transform.smoothscale(CreateThumbs(mainGame.board, mainGame.cur_player), [385,170]) #Generate thumbnails for new player (here so it is only done when the player changes, not every frame change)

            if mainGame.countActivePlayers() < 2:
                mainGame.advancePlayer()
                msgBox = MessageBox(screen, mainGame.getCurPlayer().player_name + ' has won the game.', 'Game Over')
                exitOnBoxClose = True
            
        #Button for buying a property has been clicked
        if buy_but_click and (mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.NORMAL or mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.SCHOOL or mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.STATION): #Final check that the property can actually be owned
            #Player wished to buy property
            if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getOwner() == -1: #Property is unowned, hence can actually be bought
                if mainGame.getCurPlayer().player_money >=  mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getCost():
                    #Player has enough money
                    mainGame.getCurPlayer().spendMoney(mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getCost()) #Decrease the player's bank balance accordingly
                    mainGame.board.getProp(mainGame.getCurPlayer().player_pos).buyProperty(mainGame.cur_player) #Change the property's status to track the new ownership
                    mainGame.prop_thumbs = pygame.transform.smoothscale(CreateThumbs(mainGame.board, mainGame.cur_player), [385,170]) #Update title deed thumbnails to reflect newly purchased properties
        
        #Button to apply the effects of a Pot Luck or Council Chest card
        if use_card_but_click and mainGame.controller.cur_card != None: #Check there is a card to work with
            mainGame.controller.card_used = True
            applyCardEffects(mainGame, mainGame.controller.card_effs) #Apply card effects

        #All of the following may only be done if the current player owns the property
        #Button for mortgaging or unmortgaging a property
        if mort_but_click and (mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.NORMAL or mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.SCHOOL or mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.STATION): #Final check that the property is one that may be mortgaged
            if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getOwner() == mainGame.cur_player and mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getMortgageStatus() == False: #Property must be owned by the current player and not already mortgaged
                mainGame.board.getProp(mainGame.getCurPlayer().player_pos).setMortgageStatus(True) #Property is now mortgaged
                mainGame.getCurPlayer().addMoney(int(mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getMortgageVal()))
            elif mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getOwner() == mainGame.cur_player and mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getMortgageStatus(): #Property must be owned by the current player and is mortgaged
                if mainGame.getCurPlayer().player_money >= mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getMortgageVal() * 1.2: #Player has sufficient money to unmortgage the property (twice the money gotten by mortgaging it)
                    mainGame.board.getProp(mainGame.getCurPlayer().player_pos).setMortgageStatus(False) #Property is no longer in a state of being mortgaged
                    mainGame.getCurPlayer().spendMoney(int(mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getMortgageVal() * 1.2)) #Decrease player's money by the cost of unmortgaging the property
        
        #Button for buying a Council House or Tower Block
        if buy_upgrade_but_click and mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.NORMAL and wholeGroupOwned(mainGame.board, mainGame.cur_player, mainGame.getCurPlayer().player_pos): #Player wishes to upgrade the property and said upgrade can actually be purchaed
            if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getOwner() == mainGame.cur_player: #May only be bought if the property is owned by the current player     
                if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getCH() < 4: #Fewer than 4  Council Houses, so these are the next upgrade to be bought 
                    if mainGame.getCurPlayer().player_money >= (mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getCHCost() * countGroupSize(mainGame.board, mainGame.cur_player, mainGame.getCurPlayer().player_pos)): #Player actually has enough money to buy the Council House upgrade
                        buyCHGroup(mainGame.board, mainGame.cur_player, mainGame.getCurPlayer().player_pos) #Buy the Council Houses for the whole group
                        mainGame.getCurPlayer().spendMoney(mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getCHCost() * countGroupSize(mainGame.board, mainGame.cur_player, mainGame.getCurPlayer().player_pos)) #Decrease the player's money by the cost of a Council House for however many properties are in the group
                elif mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getCH() == 4 and mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getTB() == 0: #4 Council Houses and no Tower Blocks, so Tower Block can be bought 
                    if mainGame.getCurPlayer().player_money >= (mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getTBCost() * countGroupSize(mainGame.board, mainGame.cur_player, mainGame.getCurPlayer().player_pos)): #Player actually has enough money to buy the Tower Block upgrade
                        buyTBGroup(mainGame.board, mainGame.cur_player, mainGame.getCurPlayer().player_pos) #Buy the Council Houses for the whole group
                        mainGame.getCurPlayer().spendMoney(mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getTBCost() * countGroupSize(mainGame.board, mainGame.cur_player, mainGame.getCurPlayer().player_pos)) #Decrease the player's money by the cost of a Tower Block for however many properties are in the group

        #Button for selling a Council House or Tower Block
        if sell_upgrade_but_click and mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getType() == Prop_Type.NORMAL and wholeGroupOwned(mainGame.board, mainGame.cur_player, mainGame.getCurPlayer().player_pos): #Player wishes to upgrade the property and said upgrade can actually be purchaed
            if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getOwner() == mainGame.cur_player: #May only be bought if the property is owned by the current player     
                if mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getTB() > 0: #Property has a Tower Block that can be sold
                    sellTBGroup(mainGame.board, mainGame.cur_player, mainGame.getCurPlayer().player_pos) #Sell the Tower Blocks for the whole group
                    mainGame.getCurPlayer().addMoney(int(mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getTBCost()/2 * countGroupSize(mainGame.board, mainGame.cur_player, mainGame.getCurPlayer().player_pos))) #Increase the player's money by half of what the upgrades were bought for
                elif mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getCH() > 0: #No Tower Blocks, buy some Council Houses which can instead be sold 
                    sellCHGroup(mainGame.board, mainGame.cur_player, mainGame.getCurPlayer().player_pos) #Sell the Council Houses for the whole group
                    mainGame.getCurPlayer().addMoney(int(mainGame.board.getProp(mainGame.getCurPlayer().player_pos).getCHCost()/2 * countGroupSize(mainGame.board, mainGame.cur_player, mainGame.getCurPlayer().player_pos))) #Increase the player's money by half of what the upgrades were bought for

        #Button to buy a map out of Bogside for £50
        if leave_bogside_but_click and (mainGame.getCurPlayer().player_money >= 50 or mainGame.getCurPlayer().player_hasBogMap) and mainGame.getCurPlayer().player_inJail:
            mainGame.getCurPlayer().leaveJail()
            if mainGame.getCurPlayer().player_hasBogMap == False:
                mainGame.getCurPlayer().spendMoney(50)
            else:
                mainGame.getCurPlayer().useBogMap()

        if msgBox != None:
            msgBox.update()
            if msgBox.should_exit == False:
                msgBox.draw(screen)
            
        #Reset button booleans so that effects of clicking buttons do not happen more than once
        dice_but_click = False
        turn_but_click = False
        buy_but_click = False
        mort_but_click = False
        buy_upgrade_but_click = False
        sell_upgrade_but_click = False
        leave_bogside_but_click = False
        use_card_but_click = False
        clock.tick(fps) #10 fps currently, but could easily be changed to update more or less often
        pygame.display.flip() #Refresh display from a pygame perspective, to reflect the screen.blit()s
    return mainGame, gotoScreen #Pass the Game object and the integer storing where the game will go to next back out to the main game loop

#------------------------------Property Details Code------------------------------
def PropDetails(mainGame):
    font_40 = pygame.font.SysFont('Arial', 40) #Font for title, money and exit button
    font_20 = pygame.font.SysFont('Arial', 20) #Font for actual property details
    font_20b = pygame.font.SysFont('Arial', 20, True) #Font for column headings
    font_16 = pygame.font.SysFont('Arial', 16) #Font for button captions

    props_owned = countPropsOwned(mainGame.board, mainGame.cur_player)
    board_poses = setupBoardPoses(mainGame.board, mainGame.cur_player, props_owned) #Array containing the board positions of all of the current player's owned properties

    #Initialise button arrays
    buy_buts = np.array([None] * props_owned)
    sell_buts = np.array([None] * props_owned)
    mort_buts = np.array([None] * props_owned)
    deed_buts = np.array([None] * props_owned)
    exit_but = pygame.Rect(880,10,120,50)
    
    y_top = 90 #First y co-ordinate for a row of details
    y_space = 30 #Co-ordinate spacing between rows

    #Setup buttons (one element of each array for each property)
    for counter in range(props_owned):
        buy_buts[counter] = pygame.Rect(500,y_top + y_space*counter,60,25)
        sell_buts[counter] = pygame.Rect(565,y_top + y_space*counter,60,25)
        mort_buts[counter] = pygame.Rect(630,y_top + y_space*counter,60,25)
        deed_buts[counter] = pygame.Rect(695,y_top + y_space*counter,75,25)
    
    fps = 10
    cur_deed = None #Image for a title deed that is being displayed at any one moment
    deed_prop = -1 #Board position of the property whose title deed is currently being shown
    buy_but_click = -1  #Variables storing when buttons are clicked
    sell_but_click = -1 #-1 indicates not clicked for this iteration
    mort_but_click = -1 #Not -1 indicates the integer contents of the variable is the row of whatever of the four types of button was clicked (zero-indexed)
    deed_but_click = -1

    prop_details_running = True
    while prop_details_running: #Main loop for this part of the program
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                prop_details_running = False
                gotoScreen = -1
            if event.type == pygame.KEYDOWN: #If any key pressed
                if event.key == pygame.K_ESCAPE: #Escape key exits the game
                    prop_details_running = False
                    gotoScreen = -1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #Left mouse button
                    mouse_pos = event.pos #Position of the cursor when nouse was clicked
                    if exit_but.collidepoint(mouse_pos):
                        prop_details_running = False
                        gotoScreen = 1
                    for counter in range(props_owned): #Cycle through all the arrays of buttons ot see if any have been clicked
                        if buy_buts[counter].collidepoint(mouse_pos):
                            buy_but_click = counter
                        if sell_buts[counter].collidepoint(mouse_pos):
                            sell_but_click = counter
                        if mort_buts[counter].collidepoint(mouse_pos):
                            mort_but_click = counter
                        if deed_buts[counter].collidepoint(mouse_pos):
                            deed_but_click = counter

        screen.fill((255,255,255))
        
        tit_text = font_40.render('Viewing Property Details:', True, (0,0,0)) #Render title at top left of screen
        screen.blit(tit_text, [10, 0])

        displayButtonRect(exit_but, (100, 100, 100), font_40, 'Exit', (0, 0, 0)) #Exit button at top right of screen
        
        mon_text = font_40.render('£' + str(mainGame.getCurPlayer().player_money), True, (0,0,0)) #Render player money on screen
        f_width, f_height = font_40.size('£' + str(mainGame.getCurPlayer().player_money))
        screen.blit(mon_text, [(770-f_width), 0])

        pygame.draw.rect(screen, (0,0,0), pygame.Rect(10,50,770,700), 10) #Draw black rectangle surrounding the property data

        #Display each of the column headings (bold text)
        head_1 = font_20b.render('Property', True, (0,0,0))
        screen.blit(head_1, [30, 60])
        head_2 = font_20b.render('Group', True, (0,0,0))
        screen.blit(head_2, [200, 60])
        head_3 = font_20b.render('Rent (£)', True, (0,0,0))
        screen.blit(head_3, [260, 60])
        head_4 = font_20b.render('Mortgage(£)', True, (0,0,0))
        screen.blit(head_4, [330, 60])
        head_5 = font_20b.render('CH/TB', True, (0,0,0))
        screen.blit(head_5, [440, 60])
        head_6 = font_20b.render('Options', True, (0,0,0))
        screen.blit(head_6, [640, 60])

        if cur_deed != None: #Can only display a chosen title deed if one has already been chosen
            screen.blit(cur_deed, [790, 200])

        y_pos = y_top #Y co-ordinate of the first row of data
        for counter in range(props_owned):
            text_1 = font_20.render(mainGame.board.getProp(board_poses[counter]).getTitle(), True, (0,0,0)) #Property name/title
            screen.blit(text_1, [30, y_pos])
            
            if mainGame.board.getProp(board_poses[counter]).getType() == Prop_Type.NORMAL: #SCHOOL and STATION properties have no 'Group Colour', Council Houses or Tower Blocks
                pygame.draw.rect(screen, mainGame.board.getProp(board_poses[counter]).getGroupCol(), pygame.Rect(200,y_pos,30,20))

                show_rent = mainGame.board.getProp(board_poses[counter]).getRent()
                if wholeGroupOwned(mainGame.board, mainGame.cur_player, board_poses[counter]) and mainGame.board.getProp(board_poses[counter]).getCH() == 0:
                    show_rent = show_rent * 2
                text_2 = font_20.render(str(show_rent), True, (0,0,0))
                screen.blit(text_2, [260, y_pos])
                text_4 = font_20.render(str(mainGame.board.getProp(board_poses[counter]).getCH()) + '/' + str(mainGame.board.getProp(board_poses[counter]).getTB()), True, (0,0,0))
                screen.blit(text_4, [440, y_pos])

            text_3 = font_20.render(str(mainGame.board.getProp(board_poses[counter]).getMortgageVal()), True, (0,0,0)) #Mortgage value of the property
            screen.blit(text_3, [330, y_pos])

            y_pos += y_space #Increment y co-ordinate variable by the difference in co-ordinates between each row, as already defined

            if wholeGroupOwned(mainGame.board, mainGame.cur_player, board_poses[counter]):
                if mainGame.board.getProp(board_poses[counter]).getCH() < 4: #Council Houses are still available to buy
                    displayButtonRect(buy_buts[counter], (100, 100, 100), font_16, 'Buy CH', (0, 0, 0))
                elif mainGame.board.getProp(board_poses[counter]).getTB() == 0: #Player may still buy a Tower Block
                    displayButtonRect(buy_buts[counter], (100, 100, 100), font_16, 'Buy TB', (0, 0, 0))

                if mainGame.board.getProp(board_poses[counter]).getTB() > 0: #Player has Tower Blocks available to sell
                    displayButtonRect(sell_buts[counter], (100, 100, 100), font_16, 'Sell TB', (0, 0, 0))
                elif mainGame.board.getProp(board_poses[counter]).getCH() > 0: #Player has no Tower Blocks, but still has Council Houses which may be sold
                    displayButtonRect(sell_buts[counter], (100, 100, 100), font_16, 'Sell CH', (0, 0, 0))

            if mainGame.board.getProp(board_poses[counter]).getMortgageStatus(): #Properrty is mortgaged, thus it can only be bought back
                displayButtonRect(mort_buts[counter], (100, 100, 100), font_16, 'Buy-Back', (0, 0, 0))
            else: #Property may be mortgaged as it is not currently mortgaged
                displayButtonRect(mort_buts[counter], (100, 100, 100), font_16, 'Mortgage', (0, 0, 0))
   
            displayButtonRect(deed_buts[counter], (100, 100, 100), font_16, 'View Deed', (0, 0, 0))

        if mort_but_click != -1: #One of the mortgaging buttons has been clicked
            if mainGame.board.getProp(board_poses[mort_but_click]).getMortgageStatus() == False: #Unmortgaged
                mainGame.board.getProp(board_poses[mort_but_click]).setMortgageStatus(True) #Mortgage property
                mainGame.getCurPlayer().addMoney(mainGame.board.getProp(board_poses[mort_but_click]).getMortgageVal()) #Increase the player's money by the mortgage value of the property
            else: #Mortgaged already
                if mainGame.getCurPlayer().player_money >= mainGame.board.getProp(board_poses[mort_but_click]).getMortgageVal() * 1.2: #If the player has 120% of the mortgage value of the property (this is the buy-back cost)
                    mainGame.board.getProp(board_poses[mort_but_click]).setMortgageStatus(False) #Unmortgage the property
                    mainGame.getCurPlayer().spendMoney(int(mainGame.board.getProp(board_poses[mort_but_click]).getMortgageVal() * 1.2)) #Debit the player's money by 120% of the mortgage value
            if deed_prop == board_poses[mort_but_click]: #If title deed has changed 
                cur_deed = pygame.transform.smoothscale(mainGame.board.getProp(board_poses[mort_but_click]).getTitleDeed(), [225,400])

        if deed_but_click != -1: #One of the buttons for viewing a title deed has been clicked
            cur_deed = pygame.transform.smoothscale(mainGame.board.getProp(board_poses[deed_but_click]).getTitleDeed(), [225,400]) #Scale title deed so it fits in the narrow sidebar
            deed_prop = board_poses[deed_but_click]

        if buy_but_click != -1: #One of the buttons for buying CH or TB has been clicked
            if mainGame.board.getProp(board_poses[buy_but_click]).getCH() < 4: #Fewer than 4  Council Houses, so these are the next upgrade to be bought 
                if mainGame.getCurPlayer().player_money >= (mainGame.board.getProp(board_poses[buy_but_click]).getCHCost() * countGroupSize(mainGame.board, mainGame.cur_player, board_poses[buy_but_click])): #Player actually has enough money to buy the Council House upgrade
                    buyCHGroup(mainGame.board, mainGame.cur_player, board_poses[buy_but_click]) #Buy the Council Houses for the whole group
                    mainGame.getCurPlayer().spendMoney(mainGame.board.getProp(board_poses[buy_but_click]).getCHCost() * countGroupSize(mainGame.board, mainGame.cur_player, board_poses[buy_but_click])) #Decrease the player's money by the cost of a Council House for however many properties are in the group
            elif mainGame.board.getProp(board_poses[buy_but_click]).getCH() == 4 and mainGame.board.getProp(board_poses[buy_but_click]).getTB() == 0: #4 Council Houses and no Tower Blocks, so Tower Block can be bought 
                if mainGame.getCurPlayer().player_money >= (mainGame.board.getProp(board_poses[buy_but_click]).getTBCost() * countGroupSize(mainGame.board, mainGame.cur_player, board_poses[buy_but_click])): #Player actually has enough money to buy the Tower Block upgrade
                    buyTBGroup(mainGame.board, mainGame.cur_player, board_poses[buy_but_click]) #Buy the Council Houses for the whole group
                    mainGame.getCurPlayer().spendMoney(mainGame.board.getProp(board_poses[buy_but_click]).getTBCost() * countGroupSize(mainGame.board, mainGame.cur_player, board_poses[buy_but_click])) #Decrease the player's money by the cost of a Tower Block for however many properties are in the group

        if sell_but_click != -1: #One of the buttons for selling CH or TB has been clicked
            if mainGame.board.getProp(board_poses[sell_but_click]).getTB() > 0: #Property has a Tower Block that can be sold
                sellTBGroup(mainGame.board, mainGame.cur_player, board_poses[sell_but_click]) #Sell the Tower Blocks for the whole group
                mainGame.getCurPlayer().addMoney(int(mainGame.board.getProp(board_poses[sell_but_click]).getTBCost()/2 * countGroupSize(mainGame.board, mainGame.cur_player, board_poses[sell_but_click]))) #Increase the player's money by half of what the upgrades were bought for
            elif mainGame.board.getProp(board_poses[sell_but_click]).getCH() > 0: #No Tower Blocks, buy some Council Houses which can instead be sold 
                sellCHGroup(mainGame.board, mainGame.cur_player, board_poses[sell_but_click]) #Sell the Council Houses for the whole group
                mainGame.getCurPlayer().addMoney(int(mainGame.board.getProp(board_poses[sell_but_click]).getCHCost()/2 * countGroupSize(mainGame.board, mainGame.cur_player, board_poses[sell_but_click]))) #Increase the player's money by half of what the upgrades were bought for

        #Reset all button variables so the actions of buttons only happen once
        buy_but_click = -1
        sell_but_click = -1
        mort_but_click = -1
        deed_but_click = -1
        clock.tick(fps) #10 fps currently, but could easily be changed to update more or less often
        pygame.display.flip() #Refresh display from a pygame perspective, to reflect the screen.blit()s
    return mainGame, gotoScreen #Pass the Game object and the integer storing where the game will go to next back out to the main game loop


#------------------------------Leaderboards Code------------------------------
def Leaderboards(mainGame):
    font_48 = pygame.font.SysFont('Arial', 48) #Font for title and name
    font_40 = pygame.font.SysFont('Arial', 40) #Font for the "?" and Exit buttons
    font_28 = pygame.font.SysFont('Arial', 28) #Font for actual leaderboards and attributes
    font_32b = pygame.font.SysFont('Arial', 32, True) #Font for column headings

    lead_arr = setup2DArray(mainGame)

    #Arrow images to be displayed on the buttons that are used by the player for choosing which column to sort on and whether to sort ascending or descending
    arrow_both = pygame.image.load("img/Arrows/both.png")
    arrow_up = pygame.image.load("img/Arrows/up.png")
    arrow_down = pygame.image.load("img/Arrows/down.png")
    
    #Initialise button array
    sort_buts = np.array([None] * 3)
    sort_buts[0] = pygame.Rect(360,80,40,40)
    sort_buts[1] = pygame.Rect(610,80,40,40)
    sort_buts[2] = pygame.Rect(940,80,40,40)
    
    exit_but = pygame.Rect(880,10,120,50)
    help_but = pygame.Rect(810,10,50,50)

    msgBox = MessageBox(screen, 'Total Money measures simply how much money each player has in the Bank. \n Total Assets counts the values of all owned properties, upgrades, etc. based on how much was paid for them initially. \n Obtainable Money is how much money each player could get if they were to sell off all of their properties and the like.', 'Leaderboards: Explained')
    msgBox.should_exit = True
    
    y_top = 120 #First y co-ordinate for a row of details
    y_space = 40 #Co-ordinate spacing between rows
    
    fps = 10
    sort_column = 1
    sort_asc = False
    sort_but_click = -1
    lead_arr = quickSort(lead_arr, 0, lead_arr.shape[0]-1, sort_column, sort_asc)
    
    leaderboards_running = True
    while leaderboards_running: #Main loop for this part of the program
        for event in pygame.event.get():
            msgBox.handle_input_event(event)
            if msgBox.should_exit == False:
                break
            if event.type == pygame.QUIT:
                leaderboards_running = False
                gotoScreen = -1
            if event.type == pygame.KEYDOWN: #If any key pressed
                if event.key == pygame.K_ESCAPE: #Escape key exits the game
                    leaderboards_running = False
                    gotoScreen = -1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #Left mouse button
                    mouse_pos = event.pos #Position of the cursor when nouse was clicked
                    if exit_but.collidepoint(mouse_pos):
                        leaderboards_running = False
                        gotoScreen = 1
                    if help_but.collidepoint(mouse_pos):
                        msgBox.should_exit = False
                    for counter in range(3): #Cycle through all the arrays of buttons to see if any have been clicked
                        if sort_buts[counter].collidepoint(mouse_pos):
                            sort_but_click = counter

        screen.fill((255,255,255))
        
        tit_text = font_48.render('Viewing Leaderboards:', True, (0,0,0)) #Render title at top left of screen
        screen.blit(tit_text, [10, 10])

        displayButtonRect(exit_but, (100, 100, 100), font_40, 'Exit', (0, 0, 0)) #Exit button at top right of screen
        displayButtonRect(help_but, (100, 100, 100), font_40, '?', (0, 0, 0))
        
        mon_text = font_48.render(mainGame.getCurPlayer().player_name, True, (0,0,0)) #Render player money on screen
        f_width, f_height = font_48.size(mainGame.getCurPlayer().player_name)
        screen.blit(mon_text, [(770-f_width), 10])

        pygame.draw.rect(screen, (0,0,0), pygame.Rect(10,70,1000,700), 10) #Draw black rectangle surrounding the property data

        #Display each of the column headings (bold text)
        head_1 = font_32b.render('Player', True, (0,0,0))
        screen.blit(head_1, [30, 80])
        head_2 = font_32b.render('Total Money', True, (0,0,0))
        screen.blit(head_2, [200, 80])
        head_3 = font_32b.render('Total Assets', True, (0,0,0))
        screen.blit(head_3, [450, 80])
        head_4 = font_32b.render('Obtainable Money', True, (0,0,0))
        screen.blit(head_4, [700, 80])

        for counter in range(3):
            displayButtonRect(sort_buts[counter], (100, 100, 100), font_28, '', (0, 0, 0))

            if counter == sort_column-1:
                if sort_asc:
                    screen.blit(arrow_down, [sort_buts[counter].x, sort_buts[counter].y])
                else:
                    screen.blit(arrow_up, [sort_buts[counter].x, sort_buts[counter].y])
            else:
                screen.blit(arrow_both, [sort_buts[counter].x, sort_buts[counter].y])

        y_pos = y_top #Y co-ordinate of the first row of data
        for counter in range(lead_arr.shape[0]):
            text_1 = font_28.render(mainGame.getPlayer(lead_arr[counter][0]).player_name, True, (0,0,0)) #Property name/title
            screen.blit(text_1, [30, y_pos])
            text_2 = font_28.render(str(lead_arr[counter][1]), True, (0,0,0)) 
            screen.blit(text_2, [200, y_pos])
            text_3 = font_28.render(str(lead_arr[counter][2]), True, (0,0,0)) 
            screen.blit(text_3, [450, y_pos])
            text_4 = font_28.render(str(lead_arr[counter][3]), True, (0,0,0))
            screen.blit(text_4, [700, y_pos])


            y_pos += y_space #Increment y co-ordinate variable by the difference in co-ordinates between each row, as already defined

        if sort_but_click != -1:
            if sort_column == sort_but_click+1:
                sort_asc = not sort_asc
            else:
                sort_column = sort_but_click + 1
                sort_asc = False

            lead_arr = quickSort(lead_arr, 0, lead_arr.shape[0]-1, sort_column, sort_asc)

        msgBox.update()
        if msgBox.should_exit == False:
            msgBox.draw(screen)
            
        sort_but_click = -1
        clock.tick(fps) #10 fps currently, but could easily be changed to update more or less often
        pygame.display.flip() #Refresh display from a pygame perspective, to reflect the screen.blit()s
    return mainGame, gotoScreen #Pass the Game object and the integer storing where the game will go to next back out to the main game loop

#------------------------------Pause Menu Code------------------------------ 
def PauseMenu(mainGame):
    save_file_box = TextBox((340, 300, 560, 50), clear_on_enter=False, inactive_on_enter=False, active=False, active_color=pygame.Color("red")) #Create text box for storing save file path
    save_file_box.buffer = list(mainGame.save_path) #list() is used to convert string into array of characters

    sae_button = pygame.Rect(150,425,300,80) #This lot is used for registering if mouse clicks are on a certain button
    ews_button = pygame.Rect(600,425,300,80)
    sar_button = pygame.Rect(75,620,400,80)
    rws_button = pygame.Rect(550,620,400,80)
    change_button = pygame.Rect(910,300,90,50)
    enable_button = pygame.Rect(910,360,90,50)
    resume_button = pygame.Rect(750,10,200,80)
    music_box = pygame.Rect(100,200,40,40)
    font_48 = pygame.font.SysFont('Arial', 48) #Fonts used for texts, of various sizings
    font_60 = pygame.font.SysFont('Arial', 60)
    font_40 = pygame.font.SysFont('Arial', 40)
    font_28 = pygame.font.SysFont('Arial', 28)

    msgBox = None #Will become MessageBox object as required
    
    change_but_click = False
    enable_but_click = False
    sae_but_click = False
    ews_but_click = False
    sar_but_click = False
    rws_but_click = False
    music_box_click = False
    pause_menu_running = True
    while pause_menu_running:
        for event in pygame.event.get():
            if msgBox != None: #If a MessageBox has been created
                msgBox.handle_input_event(event)
                if msgBox.should_exit == False:
                    break #Exit for loop; do not register any other objects
            if event.type == pygame.QUIT:
                pause_menu_running = False
                gotoScreen = -1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: #Escape key exits the game
                    pause_menu_running = False #This screen will no longer run
                    gotoScreen = -1 #Game will completely exit
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #Left mouse button
                    mouse_pos = event.pos #Position of the cursor when nouse was clicked
                    if resume_button.collidepoint(mouse_pos): #Button used to exit this screen/the entire game
                        pause_menu_running = False
                        gotoScreen = 1
                    if change_button.collidepoint(mouse_pos): #Button for creating the game
                        change_but_click = True
                    if enable_button.collidepoint(mouse_pos): #Button for toggling autocorrect
                        enable_but_click = True
                    if sae_button.collidepoint(mouse_pos): #Button for Save and Exit
                        sae_but_click = True
                    if ews_button.collidepoint(mouse_pos): #Button for Exit Without Saving
                        ews_but_click = True
                    if sar_button.collidepoint(mouse_pos): #Button for Save and Restart
                        sar_but_click = True
                    if rws_button.collidepoint(mouse_pos): #Button for Restart Without Saving
                        rws_but_click = True
                    if music_box.collidepoint(mouse_pos): #Check box for toggling background music
                        music_box_click = True 
            save_file_box.get_event(event) #Function that allows each textbox to register key presses and the like
            

        screen.fill((255,255,255)) #Clear the screen
        pygame.draw.rect(screen, (0,0,0), pygame.Rect(50,20,20,60))
        pygame.draw.rect(screen, (0,0,0), pygame.Rect(80,20,20,60))
        pause_title = font_60.render("The Game is Paused", True, (0,0,0)) #Display title at top of screen
        screen.blit(pause_title, [120, 10])
        displayButtonRect(resume_button, (100,100,100), font_60, 'Resume', (0,0,0)) #Display resume button at top right

        settings_txt = font_60.render("Settings:", True, (0,0,0)) #Display Settings sub-heading
        screen.blit(settings_txt, [10, 110])

        pygame.draw.rect(screen, (0,0,0), music_box, 2) #Display blank check box
        if not mainGame.pause: #If game is unpaused, check box needs to be checked
            pygame.draw.line(screen, (0,0,0), [102, 220], [115, 238], 4) #Display two lines corresponding to the two parts of a tick
            pygame.draw.line(screen, (0,0,0), [115, 238], [145, 195], 4)

        toggle_txt = font_48.render("Toggle Background Music", True, (0,0,0)) #Text next to check box
        screen.blit(toggle_txt, [150, 190])

        save_txt = font_60.render("Save Game:", True, (0,0,0)) #Save Game sub-heading
        screen.blit(save_txt, [10, 240])

        save_file_txt = font_48.render("Save File Path:", True, (0,0,0)) #Title of save path text box
        screen.blit(save_file_txt, [30, 300])
        
        save_file_box.update() #Update the textbox based on events
        save_file_box.draw(screen) #Draw the text box and contents on screen

        displayButtonRect(change_button, (100,100,100), font_28, 'Change', (0,0,0)) #Display button for updating save path
        if mainGame.autosave: #If game is set to autosave
            autosave_txt = font_48.render("Autosave is currently on", True, (0,0,0)) #Display the fact that game autosaves and hence button to disable it
            screen.blit(autosave_txt, [30, 360])
            displayButtonRect(enable_button, (100,100,100), font_28, 'Disable', (0,0,0))
        else:
            autosave_txt = font_48.render("Autosave is currently off", True, (0,0,0)) #Display the fact that game does not autosave and hence button to enable it
            screen.blit(autosave_txt, [30, 360])
            displayButtonRect(enable_button, (100,100,100), font_28, 'Enable', (0,0,0))

        displayButtonRect(sae_button, (100,100,100), font_40, 'Save and Exit', (0,0,0)) #Display the buttons related to exiting on one horizontal line
        displayButtonRect(ews_button, (100,100,100), font_40, 'Exit Without Saving', (0,0,0))

        new_txt = font_60.render("New Game:", True, (0,0,0)) #Display new game sub-heading
        screen.blit(new_txt, [10, 550])

        displayButtonRect(sar_button, (100,100,100), font_40, 'Save and Restart', (0,0,0)) #Display the buttons related to restarting on one horizontal line
        displayButtonRect(rws_button, (100,100,100), font_40, 'Restart Without Saving', (0,0,0))

        if change_but_click: #Button for updating save file path
            valid = True #Whether the file path entered is valid
            if save_file_box.getContents()[-3:].lower() != "dfo": #Must have correct file ending, or invalid
                msgBox = MessageBox(screen, 'Invalid file. Please ensure the entered file has the correct .dfo file ending.', 'File Error')
                valid = False #Path is not valid as wrong file ending

            if valid:   
                try:
                    os.makedirs(os.path.dirname(save_file_box.getContents()), exist_ok=True)
                    f = open(save_file_box.getContents(), 'w+')
                except: #Any error occurs in creating the directory or file
                    msgBox = MessageBox(screen, 'Invalid save file entered. Please ensure the path entered exists and you have permissions to access it (the file does not have to)', 'Invalid Save File')
                    valid = False #Path is not valid as cannot be created without error

            if valid:
                mainGame.save_path = save_file_box.getContents() #Update save file within the Game object
                mainGame.saveGame() #Save the game in the newly entered file

        if enable_but_click: #Button for toggline autosave feature on/off
            mainGame.autosave = not mainGame.autosave #Toggle the boolean value of autosave

        if sae_but_click: #Save and Exit
            mainGame.saveGame() #Save game
            pause_menu_running = False #This screen no longer running
            gotoScreen = -1 #Don't go to any other screen (i.e. exit completely)

        if ews_but_click:
            pause_menu_running = False #This screen no longer running
            gotoScreen = -1 #Don't go to any other screen (i.e. exit completely)

        if sar_but_click:
            mainGame.saveGame() #Save the game
            pause_menu_running = False #This screen no longer running
            gotoScreen = 0

        if rws_but_click:
            pause_menu_running = False #This screen no longer running
            gotoScreen = 0 #Goto new game screen

        if music_box_click: #Check box for background music
            """ if mainGame.pause: #Music is currently paused
                pygame.mixer.music.unpause() #Unpause music
            else: #Music is currently unpaused
                pygame.mixer.music.pause() #Pause music """
            mainGame.pause = not mainGame.pause #Toggle state of pause in Game class
         
        if msgBox != None: #If a MessageBox has been created
            msgBox.update() #Update message box with relevant events
            if msgBox.should_exit == False: #If message box should be showing
                msgBox.draw(screen) #Draw message box on screen

        change_but_click = False #Reset variable for buttons clicks so that actions only happen once
        enable_but_click = False
        sae_but_click = False
        ews_but_click = False
        sar_but_click = False
        rws_but_click = False
        music_box_click = False 
        clock.tick(10) #10 fps
        pygame.display.flip() #Refresh screen

    return mainGame, gotoScreen #Pass the Game object and the integer storing where the game will go to next back out to the main game loop
       
#------------------------------Main Game Loop------------------------------
screen = pygame.display.set_mode([1024,768])#, pygame.FULLSCREEN) #Create screen in fullscreen mode and fill white
pygame.display.set_caption('Dunfermline-opoly')
screen.fill((255,255,255))

#pygame.mixer.music.load('music.mp3') #Load in and set background music to play endlessly
#pygame.mixer.music.play(-1)

nextScreen = 0
mGame = None #Create blank object that will store the Game object
while nextScreen != -1: #Main Game Loop
    if nextScreen == 0:
        mGame, nextScreen = NewGame()
    elif nextScreen == 1: #Main Game Screen
        mGame, nextScreen = MainScreen(mGame)
    elif nextScreen == 2: #Property Details Screen
        mGame, nextScreen = PropDetails(mGame)
    elif nextScreen == 3: #Leaderboards Screen
        mGame, nextScreen = Leaderboards(mGame)
    elif nextScreen == 4: #Pause Menu
        mGame, nextScreen = PauseMenu(mGame)
    
pygame.quit() #Quits the pygame module and hence the GUI
