import pygame
from pygame.locals import *
import socket
import Pyro4
import numpy as np

from button import Button
from textbox import TextBox

from lib import CreateMortDeed, CreateTitleDeed, getCardEffects, dim
from cls_net import *

#------------------------------New Networked Game Functions------------------------------ 
def drawCheck(screen, x, y, w, h):
    draw_screen = pygame.Surface((100, 100))
    draw_screen.fill((255,255,255))
    pygame.draw.line(draw_screen, (0,0,0), [5, 50], [38, 95], 10) #Display two lines corresponding to the two parts of a tick
    pygame.draw.line(draw_screen, (0,0,0), [38, 95], [100, 0], 10)
    draw_screen = pygame.transform.smoothscale(draw_screen, [w, h])
    screen.blit(draw_screen, [x, y])

def drawCross(screen, x, y, w, h):
    draw_screen = pygame.Surface((100, 100))
    draw_screen.fill((255,255,255))
    pygame.draw.line(draw_screen, (0,0,0), [5, 5], [95, 95], 10) #Display two lines corresponding to the two lines of the cross (x)
    pygame.draw.line(draw_screen, (0,0,0), [5, 95], [95, 5], 10)
    draw_screen = pygame.transform.smoothscale(draw_screen, [w, h])
    screen.blit(draw_screen, [x, y])

def renderLobby(screen, lobby, x, y, font_tit, font_det, imgs):
    lobby_ren = lobby.getLobby()

    tit_text_1 = font_tit.render("IP", True, (0,0,0))
    tit_text_2 = font_tit.render("Name", True, (0,0,0))
    tit_text_3 = font_tit.render("Piece", True, (0,0,0))
    tit_text_4 = font_tit.render("Ready Up?", True, (0,0,0))
    tit_text_5 = font_tit.render("Start Game?", True, (0,0,0))
    screen.blit(tit_text_1, [x, y])
    screen.blit(tit_text_2, [x+200, y])
    screen.blit(tit_text_3, [x+400, y])
    screen.blit(tit_text_4, [x+525, y])
    screen.blit(tit_text_5, [x+725, y])

    for i in range(dim(lobby_ren)[0]):
        #Display name and IP of current connection
        cur_ip = font_det.render(lobby_ren[i][0], True, (0,0,0))
        cur_name = font_det.render(lobby_ren[i][1], True, (0,0,0))
        screen.blit(cur_ip, [x, y+50+30*i])
        screen.blit(cur_name, [x+200, y+50+30*i])

        #Display piece chosen by current lobby member (if one has been chosen)
        if lobby_ren[i][2] != 0: #0 is used if piece has not yet been chosen.
            screen.blit(imgs[lobby_ren[i][2]-1], [x+400, y+50+30*i])
        
        #Display check/cross for Ready Up? and Start Game?
        if lobby_ren[i][3]:
            drawCheck(screen, x+585, y+50+30*i, 30, 30)
        else:
            drawCross(screen, x+585, y+50+30*i, 30, 30)
        
        if lobby_ren[i][4]:
            drawCheck(screen, x+785, y+50+30*i, 30, 30)
        else:
            drawCross(screen, x+785, y+50+30*i, 30, 30)

def renderPieces(screen, pieces, lobby, x, y, choose_text):
    screen.blit(choose_text, [x, y-50])
    conns = lobby.getUsedPieces()
    for i in range(6):
        screen.blit(pieces[i], [x + 110*(i%3), y + 110*int(i/3)])
        for piece in conns:
            if piece-1 == i: #Piece is already chosen
                overlay = pygame.Surface((100,100), pygame.SRCALPHA)
                overlay.fill((255,255,255,196))
                screen.blit(overlay, [x + 110*(i%3), y + 110*int(i/3)]) #Semi-transparent overlay to indicate unavailable piece


#------------------------------Functions for creating localGame------------------------------ 
def createLocalPlayers(p_icons, lobby_arr): #Create Player objects using the names entered into text boxes and the corresponding icons
    new_players = np.array([None] * dim(lobby_arr)[0])

    for counter in range(dim(lobby_arr)[0]):
        p_piece = LocalPlayer_Piece(lobby_arr[counter][2], pygame.transform.smoothscale(p_icons[lobby_arr[counter][2]-1], [32, 32])) #Create piece separately
        new_players[counter] = LocalPlayer(counter, p_piece) #Now create player. 1500 is the money and 0 is the initial board position

    return new_players

#Create the decks of Pot Luck and Council Chest cards, based off of data and images loading in from external files
def createLocalDeck(deck_name, card_base_path, card_texts_path, card_data_path, deck_size):
    deck_cards = np.array([None] * deck_size) #Array of blank objects; will become array of individual Card objects
    card_effects = getCardEffects(card_texts_path)
    card_img = None #Blank object, later to become loaded-in pygame images
    text_line = ""

    fh = open(card_data_path, "r")
    for counter in range(deck_size): #Iterate up to deck_size-1
        card_img = pygame.transform.smoothscale(pygame.image.load(card_base_path + str(counter + 1) + ".png"), [330, 200]) #Images are named "Pot Luck 1.png", for example. N.B. Numbering starts at one, hence the +1
        text_line = fh.readline()
        data_array = text_line.split(",") #Values are comma-separated in the external file
        for d_count in range(len(data_array)): #Convert each of the elements in the array from String (as they will be coming from an external file) to numbers
            data_array[d_count] = int(data_array[d_count])
        
        deck_cards[counter] = LocalCard(counter+1, deck_name, card_img, card_effects, data_array)
    fh.close()

    ret_deck = LocalCard_Deck(deck_cards)
    return ret_deck

#Creates an array of properties using data from a data file at the start of the game
def createLocalProperties(file_path):
    property_arr = np.array([None]*40) #Partition numpy array with 40 elements
    fh = open(file_path, "r") #Opens the sequential file for reading
    for counter in range(40): #40 properties
        propType = int(fh.read(2)[:1]) #Reads in the first two characters in a line (one number and a separating comma) and then takes the first character. This leaves propType being an integer determining which type of property the line is for
        line_text = fh.readline() #Read in the rest of the line, where all data is for a single property
        prop_values = np.array(line_text.split(",")) #Transforms the string into an array where each comma-separated item is an indivual element

        if propType == 0: #Most common property type
            property_arr[counter] = LocalNormal_Property(prop_values, CreateTitleDeed(prop_values), CreateMortDeed(prop_values[0], int(prop_values[10])*1.2))
        elif propType == 1: #School (requires crest image for title deed)
            property_arr[counter] = LocalSchool_Property(prop_values, pygame.image.load("img/Deeds/" + str(prop_values[0]) + ".png"), CreateMortDeed(prop_values[0], int(prop_values[6])*1.2))
        elif propType == 2: #Stations (requires crest image for title deed)
            property_arr[counter] = LocalStation_Property(prop_values, pygame.image.load("img/Deeds/" + str(prop_values[0]) + ".png"), CreateMortDeed(prop_values[0], int(prop_values[4])*1.2))
        elif propType == 3: #Pot Luck card spot
            property_arr[counter] = LocalProperty(prop_values[0].strip(), Prop_Type.POT_LUCK)
        elif propType == 4: #Council Chest card spot
            property_arr[counter] = LocalProperty(prop_values[0].strip(), Prop_Type.COUNCIL_CHEST)
        elif propType == 5: #Lost In Bogside spot
            property_arr[counter] = LocalProperty(prop_values[0].strip(), Prop_Type.LOST_IN_BOGSIDE)
        elif propType == 6: #Go To Bogside space
            property_arr[counter] = LocalProperty(prop_values[0].strip(), Prop_Type.GO_TO_BOGSIDE)
        elif propType == 7: #Property that incurs a charge when landed upon
            property_arr[counter] = LocalProperty(prop_values[0].strip(), Prop_Type.PAYMENT)
        elif propType == 8: #Job Centre where the player collects money when passing it
            property_arr[counter] = LocalProperty(prop_values[0].strip(), Prop_Type.JOB_CENTRE)
        elif propType == 9: #Disabled Parking - Does nothing as of yet (and it probably never will)
            property_arr[counter] = LocalProperty(prop_values[0].strip(), Prop_Type.DISABLED_PARKING)
    fh.close()
    return property_arr #Array of 40 Property (or subclass) objects

#Create the Board object that will become part of the Game class later
def createLocalBoard(data_file_path, props_arr, Pot_Luck, Council_Chest, image_path, image_dim):
    board_img = pygame.image.load(image_path) #Load and resize board image
    board_img = pygame.transform.smoothscale(board_img, [image_dim, image_dim])
    scale_f = image_dim/768 #Used in piece positioning - formulae were created for a 768x768 board

    ret_board = LocalBoard(props_arr, Pot_Luck, Council_Chest, board_img, scale_f)
    return ret_board

#Create the final Game object - this is the main point of this screen
def createLocalGame(game_players, game_board, dice_imgs_base_paths, this_player_num):
    dice_imgs = np.array([None] * 6)
    for d_count in range(6):
        dice_imgs[d_count] = pygame.image.load(dice_imgs_base_paths + str(d_count+1) + ".png") #+1 as dice images are stored with numbers 1 to 6 in the file
    dice_arr = np.array([LocalDie(dice_imgs), LocalDie(dice_imgs)])

    ret_game = LocalGame(dice_arr, game_board, game_players, this_player_num)
    return ret_game

def findPlayerNum(lobby):
    lobby_arr = lobby.getLobby()
    for counter in range(dim(lobby_arr)[0]):
        if lobby_arr[counter][0] == socket.gethostbyname(socket.gethostname()): # Matching of connected IPs
            return counter
    return -1 # If, somehow, the IP cannot be matched up.

#------------------------------New Networked Game Method------------------------------ 
def NewNet(screen, clock):
    font_48 = pygame.font.SysFont('Arial', 48)
    font_40 = pygame.font.SysFont('Arial', 40)
    font_28 = pygame.font.SysFont('Arial', 28)

    pieces_x = 350
    pieces_y = 450

    name_box = TextBox((320, 400, 380, 50), clear_on_enter=False, inactive_on_enter=True, active=True, active_color=pygame.Color("red"))
    name_text = font_48.render("Enter your Name (max 12 characters):", True, (0,0,0))
    n_width, n_height = font_48.size("Enter your Name (max 12 characters):")
    name_button = Button(400, 460, 200, 80, "Confirm", font_48)

    ready_up_but = Button(400, 460, 200, 80, "Ready Up", font_48)
    start_game_but = Button(400, 460, 200, 80, "Start Game", font_48)
    ready_up_but.hideBut()
    start_game_but.hideBut()

    piece_rects = [None] * 6
    piece_imgs_lobby = [None] * 6
    for n in range(6):
        piece_rects[n] = pygame.Rect(pieces_x + 110*(n%3), pieces_y + 110*int(n/3), 100, 100)
        piece_imgs_lobby[n] = pygame.transform.smoothscale(pygame.image.load("img/Pieces/" + str(n+1) + ".png"), [30, 30])

    choose_text = font_40.render("Choose Your Piece:", True, (0,0,0))
    pieces_large = np.array([None] * 6) #Load 6 available player pieces
    for p_counter in range(6):
        pieces_large[p_counter] = pygame.transform.smoothscale(pygame.image.load("img/Pieces/" + str(p_counter+1) + ".png"), [100, 100]) #Load image into pygame and resize

    # Read in host (server) IP and port from file.
    # This means that the server IP and port do not have to be hard-coded.
    f = open("data/Host_Data.txt", "r")
    host_dat = f.readline().split(",")
    # Some setup code that was previously run while the screen was active.
    # Having it here instead streamlines things a bit.    
    ip_text = font_48.render("Your IP: " + socket.gethostbyname(socket.gethostname()), True, (0,0,0))
    lobby = Pyro4.Proxy("PYRO:dfo.game@" + host_dat[0] + ":" + host_dat[1]) 
    # Okay, this is actually a Game() class object, but the Lobby() part is the only part actually used here, 
    # and I wrote everything here with lobby separate first, so why bother changing it?

    ready_up_texts = [font_48.render("Waiting for players to ready up.", True, (0,0,0)),
                     font_48.render("Waiting for players to ready up..", True, (0,0,0)),
                     font_48.render("Waiting for players to ready up...", True, (0,0,0))]

    waiting_texts = [font_48.render("Waiting to start.", True, (0,0,0)),
                     font_48.render("Waiting to start..", True, (0,0,0)),
                     font_48.render("Waiting to start...", True, (0,0,0))]

    newnet_running = True
    piece_choice = -1
    piece_chosen = False
    name_chosen = False
    ready_up = False
    start_game = False
    while newnet_running:
        for event in pygame.event.get():
            if name_box.visible:
                name_box.get_event(event)
                name_button.handle_input_event(event)
            ready_up_but.handle_input_event(event)
            start_game_but.handle_input_event(event)

            if event.type == pygame.QUIT:
                newnet_running = False
                gotoScreen = -1
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: #Escape key exits the game
                    newnet_running = False #This screen will no longer run
                    gotoScreen = -1 #Game will completely exit
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #Left mouse button
                    if not piece_chosen and name_chosen:
                        for n in range(6):
                            if piece_rects[n].collidepoint(event.pos):
                                piece_choice = n

        
        screen.fill((255,255,255))

        if not name_box.visible: #Player has entered name; show lobby and following game setup
            screen.blit(ip_text, [10, 10])
            screen.blit(host_text, [10, 60])
            renderLobby(screen, lobby, 10, 110, font_40, font_28, piece_imgs_lobby)
            if not piece_chosen:
                renderPieces(screen, pieces_large, lobby, pieces_x, pieces_y, choose_text)
            ready_up_but.render(screen)
            start_game_but.render(screen)
            
            if ready_up and not start_game and not lobby.allReadyUp():
                screen.blit(ready_up_texts[int(pygame.time.get_ticks()/500) % 3], [235, 460])

            if start_game and not lobby.allReadyToStart():
                screen.blit(waiting_texts[int(pygame.time.get_ticks()/500) % 3], [375, 460])

        if name_box.visible: #Player is entering name
            name_box.update()
            name_box.draw(screen)
            name_button.render(screen)
            screen.blit(name_text, [(1024-n_width)/2, 335])
        
        if name_button.clicked():
            #Determine if the name entered is valid. Will try and do something to prevent duplicate naming...
            if len(name_box.getContents()) <=  12 and len(name_box.getContents()) != 0: #Name is valid
                #Display your IP and name, and connect to server using Pyro4 module
                host_text = font_48.render("Your Name: " + name_box.getContents(), True, (0,0,0))
                lobby.connect(socket.gethostbyname(socket.gethostname()), name_box.getContents())

                name_box.hide()
                name_chosen = True
                name_button.hideBut()

        if piece_choice != -1 and name_chosen:
            if not(piece_choice+1 in lobby.getUsedPieces()):
                lobby.setPiece(socket.gethostbyname(socket.gethostname()), piece_choice+1)
                piece_chosen = True
                ready_up_but.showBut()
            piece_choice = -1

        if ready_up_but.clicked():
            lobby.readyUp(socket.gethostbyname(socket.gethostname()))
            ready_up = True
            ready_up_but.hideBut()

        if start_game_but.clicked():
            lobby.readyToStart(socket.gethostbyname(socket.gethostname()))
            start_game = True
            start_game_but.hideBut()

        if not start_game and name_chosen and not start_game_but.visible and ready_up:
            if lobby.allReadyUp() and dim(lobby.getLobby())[0] >= 2: #May not proceed until at least two players have joined
                start_game_but.showBut()


        if start_game and name_chosen and ready_up:
            if lobby.allReadyToStart() and dim(lobby.getLobby())[0] >= 2: #At least two players required for a game (duh!)
                #Creation of localGame object first
                players = createLocalPlayers(pieces_large, lobby.getLobby()) #Create array of LocalPlayer objects
                prop_arr = createLocalProperties("data/Property Values.txt") #Create array of Property objects
                Pot_Luck_Deck = createLocalDeck("Pot Luck", "img/PL/Pot Luck ", "data/Card_Texts.txt", "data/PL Master.txt", 16) #Create Card_Deck object
                Council_Chest_Deck = createLocalDeck("Council Chest", "img/CC/Council Chest ", "data/Card_Texts.txt", "data/CC Master.txt", 16) #Create Card_Deck object
                game_board = createLocalBoard("data/Board_Data.txt", prop_arr, Pot_Luck_Deck, Council_Chest_Deck, "img/Board.png", 600) #Create Board object
                this_player_num = findPlayerNum(lobby)

                localGame = createLocalGame(players, game_board, "img/Dice/", this_player_num) #Finally create the single, cohesive Game object that is the sole purpose of this screen/part of the game
                
                if lobby.getGameSetup() == False:
                    fh = open("data/Property Values.txt", "r")
                    prop_data = fh.read()
                    lobby.setupGame(prop_data)

                newnet_running = False
                gotoScreen = 6

        clock.tick(10) #10 fps
        pygame.display.flip() #Refresh screen

    return lobby, localGame, gotoScreen
