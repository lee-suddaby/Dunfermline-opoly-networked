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

def renderLobby(screen, lobby, x, y, font_tit, font_det, imgs):
    lobby_ren = lobby.getLobby()

    tit_text_1 = font_tit.render("IP", True, (0,0,0))
    tit_text_2 = font_tit.render("Name", True, (0,0,0))
    tit_text_3 = font_tit.render("Piece", True, (0,0,0))
    screen.blit(tit_text_1, [x, y])
    screen.blit(tit_text_2, [x+200, y])
    screen.blit(tit_text_3, [x+400, y])

    for i in range(dim(lobby_ren)[0]):
        cur_ip = font_det.render(lobby_ren[i][0], True, (0,0,0))
        cur_name = font_det.render(lobby_ren[i][1], True, (0,0,0))
        screen.blit(cur_ip, [x, y+50+30*i])
        screen.blit(cur_name, [x+200, y+50+30*i])
        if lobby_ren[i][2] != 0: #0 is used if piece has not yet been chosen.
            screen.blit(imgs[lobby_ren[i][2]-1], [x+400, y+50+30*i])

def renderPieces(screen, pieces, lobby, x, y):
    conns = lobby.getUsedPieces()
    for i in range(6):
        screen.blit(pieces[i], [x + 110*(i%2), y + 110*int(i/2)])
        for piece in conns:
            if piece-1 == i: #Piece is already chosen
                overlay = pygame.Surface((100,100), pygame.SRCALPHA)
                overlay.fill((255,255,255,196))
                screen.blit(overlay, [x + 110*(i%2), y + 110*int(i/2)]) #Semi-transparent overlay to indicate unavailable piece

#------------------------------New Networked Game Method------------------------------ 
def NewNet(screen, clock):
    font_48 = pygame.font.SysFont('Arial', 48)
    font_40 = pygame.font.SysFont('Arial', 40)
    font_28 = pygame.font.SysFont('Arial', 28)

    name_box = TextBox((320, 400, 380, 50), clear_on_enter=True, inactive_on_enter=True, active=True, active_color=pygame.Color("red"))
    name_text = font_48.render("Enter your Name (max 12 chars, no commas):", True, (0,0,0))
    n_width, n_height = font_48.size("Enter your Name (max 12 chars, no commas):")
    name_button = Button(400, 460, 200, 80, "Confirm", font_48)

    piece_rects = [None] * 6
    piece_imgs_lobby = [None] * 6
    for n in range(6):
        piece_rects[n] = pygame.Rect(600 + 110*(n%2), 160 + 110*int(n/2), 100, 100)
        piece_imgs_lobby[n] = pygame.transform.smoothscale(pygame.image.load("img/Pieces/" + str(n+1) + ".png"), [30, 30])


    newnet_running = True
    piece_choice = -1
    piece_chosen = False
    name_chosen = False
    while newnet_running:
        for event in pygame.event.get():
            if name_box.visible:
                name_box.get_event(event)
                name_button.handle_input_event(event)
            if event.type == pygame.QUIT:
                newnet_running = False
                gotoScreen = -1
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: #Escape key exits the game
                    newnet_running = False #This screen will no longer run
                    gotoScreen = -1 #Game will completely exit
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #Left mouse button
                    if not piece_chosen:
                        for n in range(6):
                            if piece_rects[n].collidepoint(event.pos):
                                piece_choice = n

        
        screen.fill((255,255,255))

        if not name_box.visible: #Player has entered name; show lobby and following game setup
            screen.blit(ip_text, [10, 10])
            screen.blit(host_text, [10, 60])
            screen.blit(choose_text, [600, 110])
            renderLobby(screen, lobby, 10, 110, font_40, font_28, piece_imgs_lobby)
            if not piece_chosen:
                renderPieces(screen, pieces, lobby, 600, 160)

        if name_box.visible: #Player is entering name
            name_box.update()
            name_box.draw(screen)
            name_button.render(screen)
            screen.blit(name_text, [(1024-n_width)/2, 335])
        
        if name_button.clicked():
            #Determine if the name entered is valid. Will try and do something to prevent duplicate naming...
            if not("," in name_box.getContents()) and len(name_box.getContents()) <=  12: #Name is valid
                #Display your IP and name, and connect to server using Pyro4 module
                ip_text = font_48.render("Your IP: " + socket.gethostbyname(socket.gethostname()), True, (0,0,0))
                host_text = font_48.render("Your Name: " + name_box.getContents(), True, (0,0,0))
                lobby = Pyro4.Proxy("PYRONAME:dfo.lobby")
                lobby.connect(socket.gethostbyname(socket.gethostname()), name_box.getContents())

                name_box.hide()

                choose_text = font_40.render("Choose Your Piece:", True, (0,0,0))
                pieces = np.array([None] * 6) #Load 6 available player pieces
                for p_counter in range(6):
                    pieces[p_counter] = pygame.transform.smoothscale(pygame.image.load("img/Pieces/" + str(p_counter+1) + ".png"), [100, 100]) #Load image into pygame and resize
                name_chosen = True

        if piece_choice != -1 and name_chosen:
            if not(piece_choice+1 in lobby.getUsedPieces()):
                lobby.setPiece(socket.gethostbyname(socket.gethostname()), piece_choice+1)
            piece_choice = -1
            piece_chosen = True


        clock.tick(10) #10 fps
        pygame.display.flip() #Refresh screen

    return gotoScreen
