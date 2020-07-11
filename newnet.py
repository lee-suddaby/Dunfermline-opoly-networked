import pygame
from pygame.locals import *
import socket
import Pyro4
import numpy as np

from cls import Button
from textbox import TextBox

#------------------------------New Networked Game Functions------------------------------ 
def dim(a): #Function to determine the dimensions of a python list
    if not type(a) == list:
        return []
    return [len(a)] + dim(a[0])

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

#------------------------------New Networked Game Method------------------------------ 
def NewNet(screen, clock):
    font_48 = pygame.font.SysFont('Arial', 48)
    font_40 = pygame.font.SysFont('Arial', 40)
    font_28 = pygame.font.SysFont('Arial', 28)

    pieces_x = 350
    pieces_y = 450

    name_box = TextBox((320, 400, 380, 50), clear_on_enter=False, inactive_on_enter=True, active=True, active_color=pygame.Color("red"))
    name_text = font_48.render("Enter your Name (max 12 chars, no commas):", True, (0,0,0))
    n_width, n_height = font_48.size("Enter your Name (max 12 chars, no commas):")
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

    # Some setup code that was previously run while the screen was active.
    # Having it here instead streamlines things a bit.    
    ip_text = font_48.render("Your IP: " + socket.gethostbyname(socket.gethostname()), True, (0,0,0))
    lobby = Pyro4.Proxy("PYRONAME:dfo.lobby")

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
            
            if start_game:
                screen.blit(waiting_texts[int(pygame.time.get_ticks()/500) % 3], [375, 460])

        if name_box.visible: #Player is entering name
            name_box.update()
            name_box.draw(screen)
            name_button.render(screen)
            screen.blit(name_text, [(1024-n_width)/2, 335])
        
        if name_button.clicked():
            #Determine if the name entered is valid. Will try and do something to prevent duplicate naming...
            if not("," in name_box.getContents()) and len(name_box.getContents()) <=  12 and len(name_box.getContents()) != 0: #Name is valid
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
            if lobby.allReadyUp():
                start_game_but.showBut()

        clock.tick(10) #10 fps
        pygame.display.flip() #Refresh screen

    return gotoScreen
