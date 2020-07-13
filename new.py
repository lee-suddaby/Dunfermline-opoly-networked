import pygame
from pygame.locals import *
import numpy as np
import os #Used for creating directories
import getpass #Used for getting the user's username, needed for choosing the directory of save files
from datetime import datetime #Getting the current date and time as understood by humans (rather than UNIX time)

from textbox import TextBox
from msgbox import MessageBox
from cls import *
from button import Button
from lib import getFileLines

#------------------------------New Game Functions------------------------------
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

def createPlayers(p_icons, boxes, board_dim, data_file_path): #Create Player objects using the names entered into text boxes and the corresponding icons
    fh = open(data_file_path, "r")
    init_mon = int(fh.readline())
    fh.close()
    
    player_temp = Player(0, None, 0, "")
    new_players = np.array([None] * countNames(boxes))
    p_counter = 0 #Stores which element in the new_players array is next to be instantiated
    for b_counter in range(6):
        if len(boxes[b_counter].getContents()) > 0: #Name must have been entered for a player to come into existence
            p_piece = Player_Piece(player_temp.calcPieceX(0, board_dim/768), player_temp.calcPieceY(0, board_dim/768), pygame.transform.smoothscale(p_icons[b_counter], [32, 32]), b_counter) #Create piece separately
            new_players[p_counter] = Player(init_mon, p_piece, 0, boxes[b_counter].getContents()) #Now create player. 1500 is the money and 0 is the initial board position
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
    player_temp = Player(0, None, 0, "")
    for counter in range(len(new_players)):
        p_piece = Player_Piece(player_temp.calcPieceX(int(load_arr[counter+1][2]), 600/768), player_temp.calcPieceY(int(load_arr[counter+1][2]), 600/768), pygame.transform.smoothscale(pygame.image.load('img/Pieces/' + str(int(load_arr[counter+1][3])+1) + '.png'), [32, 32]), int(load_arr[counter+1][3])) #Create piece separately. load-arr[counter+1][3] stores a number from 0-5 relating to which of the token images is used (1.png - 6.png)
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


#------------------------------New Game Method------------------------------ 
def NewGame(screen, clock):
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

    font_48 = pygame.font.SysFont('Arial', 48) #Fonts used for texts
    font_60 = pygame.font.SysFont('Arial', 60)

    new_game_title = font_60.render("New Game:", True, (0,0,0))
    icon_title = font_48.render("Enter Player Names (max 12 characters)", True, (0,0,0))
    save_title = font_48.render("Save File Path:", True, (0,0,0))

    new_buts = [Button(150, 650, 300, 80, 'Create Game', font_60), #Create Game
                Button(600, 650, 300, 80, 'Load Game', font_60), #Load Game
                Button(870, 20, 120, 70, 'Exit', font_48), #Exit
                Button(935, 100, 55, 55, '?', font_48)] #Info

    msgBox = None
    
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

            for but in new_buts:
                but.handle_input_event(event)
            for box in box_arr: 
                box.get_event(event) #Function that allows each textbox to register key presses and the like
            save_path_box.get_event(event)
            

        screen.fill((255,255,255)) #Clear the screen

        for but in new_buts: #Display buttons
            but.render(screen)

        #Display pure text aspects of the screen
        screen.blit(new_game_title, [10, 10])
        screen.blit(icon_title, [30, 75])
        screen.blit(save_title, [50, 545])
        
        for box in box_arr:
            box.update() #To do with internal workings - take clicks, key pressed etc. into account
            box.draw(screen)   #Display the boxes on screen - one of the TextBox classes methods 
        save_path_box.update() #Do the same as above but for the object that is not part of the array
        save_path_box.draw(screen)

        for piece_count in range(6): #Display the 6 pieces on screen to the left of the relevant text box
            screen.blit(pieces[piece_count], [45 + 500*(piece_count%2), 175 + 55*int(piece_count/2)])

        if new_buts[3].clicked():
            msgBox = MessageBox(screen, 'Bottle: A common and very possibly-alcoholic beverage enjoyed often enjoyed by Dunfermine residents (only those over 18 of course). \n Can: A popular soft drink that definitely does not infringe upon any Intellectual Property Rights. \n Coal: Coal mining was a prosperous (albeit dangerous) industry  for hundreds of years in the Dunfermline and Fife area. \n Crown: Dunfermline is a royal burgh. \n Badly-drawn Sheep: Sheep farming is very common in the Dunfermline area. \n Battleship: Dunfermline is situated near to the Royal Navy dockyard in Rosyth.', 'Token Info')

        if new_buts[2].clicked():
            screen_running = False
            gotoScreen = -1

        if new_buts[0].clicked(): #If button to create the game itself was clicked
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
                    players = createPlayers(pieces, box_arr, 600, "data/Player_Data.txt") #Create array of Player objects
                    prop_arr = LoadProperties("data/Property Values.txt") #Create array of Property objects
                    Pot_Luck_Deck = createDeck("Pot Luck", "img/PL/Pot Luck ", "data/Card_Texts.txt", "data/PL Master.txt", 16) #Create Card_Deck object
                    Council_Chest_Deck = createDeck("Council Chest", "img/CC/Council Chest ", "data/Card_Texts.txt", "data/CC Master.txt", 16) #Create Card_Deck object
                    game_board = createBoard("data/Board_Data.txt", prop_arr, Pot_Luck_Deck, Council_Chest_Deck, "img/Board.png", 600) #Create Board object

                    mainGame = createGame(players, game_board, save_path_box.getContents(), "img/Dice/") #Finally create the single, cohesive Game object that is the sole purpose of this screen/part of the game
                    
                    screen_running = False
                    gotoScreen = 1 #1=Main game screen
                else:
                    msgBox = MessageBox(screen, 'The names you entered are invalid. Please ensure all names are 12 characters or less, different (this part is not case-sensitive) and you have entered at least two user names', 'Invalid Usernames')                    

        if new_buts[1].clicked():
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
                    if game_board.getProp(int(data_arr[counter][0])).prop_type == Prop_Type.NORMAL:
                        game_board.getProp(int(data_arr[counter][0])).buyProperty(int(data_arr[counter][1]))
                        game_board.getProp(int(data_arr[counter][0])).C_Houses = int(data_arr[counter][2])
                        game_board.getProp(int(data_arr[counter][0])).T_Blocks = int(data_arr[counter][3])
                        game_board.getProp(int(data_arr[counter][0])).mortgage_status = bool(int(data_arr[counter][4]))
                    elif game_board.getProp(int(data_arr[counter][0])).prop_type == Prop_Type.STATION or game_board.getProp(int(data_arr[counter][0])).prop_type == Prop_Type.SCHOOL:
                        game_board.getProp(int(data_arr[counter][0])).buyProperty(int(data_arr[counter][1]))
                        game_board.getProp(int(data_arr[counter][0])).mortgage_status = bool(int(data_arr[counter][2]))
                    
                mainGame = createGame(players, game_board, save_path_box.getContents(), "img/Dice/") #Finally create the single, cohesive Game object that is the sole purpose of this screen/part of the game
                mainGame.cur_player = int(data_arr[0][0]) #Positions in array as per the order of saving, which can be seen in the method within the Game class
                mainGame.autosave = bool(int(data_arr[0][2]))
                
                screen_running = False
                gotoScreen = 1 #1=Main game screen            
          
        if msgBox != None:
            msgBox.update()
            if msgBox.should_exit == False:
                msgBox.draw(screen)

        clock.tick(30) #30 fps
        pygame.display.flip() #Refresh screen

    return mainGame, gotoScreen #Pass the Game object and the integer storing where the game will go to next back out to the main game loop
