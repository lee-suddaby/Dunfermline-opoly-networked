import pygame
from pygame.locals import *
import socket
import Pyro4

from cls import Button
from textbox import TextBox

#------------------------------New Networked Game Functions------------------------------ 
def dim(a): #Function to determine the dimensions of a python list
    if not type(a) == list:
        return []
    return [len(a)] + dim(a[0])

def renderLobby(screen, lobby, x, y, font_tit, font_det):
    lobby_ren = lobby.getLobby()

    tit_text_1 = font_tit.render("IP", True, (0,0,0))
    tit_text_2 = font_tit.render("Name", True, (0,0,0))
    screen.blit(tit_text_1, [x, y])
    screen.blit(tit_text_2, [x+200, y])

    for i in range(dim(lobby_ren)[0]):
        cur_ip = font_det.render(lobby_ren[i][0], True, (0,0,0))
        cur_name = font_det.render(lobby_ren[i][1], True, (0,0,0))
        screen.blit(cur_ip, [x, y+50+30*i])
        screen.blit(cur_name, [x+200, y+50+30*i])

#------------------------------New Networked Game Method------------------------------ 
def NewNet(screen, clock):
    font_48 = pygame.font.SysFont('Arial', 48)
    font_40 = pygame.font.SysFont('Arial', 40)
    font_28 = pygame.font.SysFont('Arial', 28)

    name_box = TextBox((320, 400, 380, 50), clear_on_enter=True, inactive_on_enter=True, active=True, active_color=pygame.Color("red"))
    name_text = font_48.render("Enter your Name (max 12 chars, no commas):", True, (0,0,0))
    n_width, n_height = font_48.size("Enter your Name (max 12 chars, no commas):")
    name_button = Button(400, 460, 200, 80, "Confirm", font_48)

    newnet_running = True
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
        
        screen.fill((255,255,255))

        if not name_box.visible: #Player has entered name; show lobby and following game setup
            screen.blit(ip_text, [10, 10])
            screen.blit(host_text, [10, 60])
            renderLobby(screen, lobby, 10, 110, font_40, font_28)

        if name_box.visible: #Player is entering name
            name_box.update()
            name_box.draw(screen)
            name_button.render(screen)
            screen.blit(name_text, [(1024-n_width)/2, 335])
        
        if name_button.clicked():
            #Determine if the name entered is valid. Will try and do something to prevent duplicate naming...
            if not("," in name_box.getContents()) and len(name_box.getContents()) <=  12: #Name is valid
                ip_text = font_48.render("Your IP: " + socket.gethostbyname(socket.gethostname()), True, (0,0,0))
                host_text = font_48.render("Your Name: " + name_box.getContents(), True, (0,0,0))
                lobby = Pyro4.Proxy("PYRONAME:dfo.lobby")
                lobby.connect(socket.gethostbyname(socket.gethostname()), name_box.getContents())

                name_box.hide()

        clock.tick(10) #10 fps
        pygame.display.flip() #Refresh screen

    return gotoScreen
