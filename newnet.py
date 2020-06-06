import pygame
from pygame.locals import *
import socket
import Pyro4

from cls import Button

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

    ip_text = font_48.render("Your IP: " + socket.gethostbyname(socket.gethostname()), True, (0,0,0))
    host_text = font_48.render("Your Name: " + socket.gethostname(), True, (0,0,0))
    lobby = Pyro4.Proxy("PYRONAME:dfo.lobby")
    lobby.connect(socket.gethostbyname(socket.gethostname()), socket.gethostname())

    newnet_running = True
    while newnet_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                newnet_running = False
                gotoScreen = -1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: #Escape key exits the game
                    newnet_running = False #This screen will no longer run
                    gotoScreen = -1 #Game will completely exit
        
        screen.fill((255,255,255))
        screen.blit(ip_text, [10, 10])
        screen.blit(host_text, [10, 60])
        renderLobby(screen, lobby, 10, 110, font_40, font_28)

        clock.tick(10) #10 fps
        pygame.display.flip() #Refresh screen

    return gotoScreen
