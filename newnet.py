import pygame
from pygame.locals import *
import numpy as np
import socket

from cls import Button

#------------------------------Lobby and Conn Classes------------------------------ 
class Lobby():
    def __init__(self):
        self.conns = list()

    def getLobby(self):
        ret_lobby = np.zeros((len(self.conns),2), str)
        for i in range(len(self.conns)):
            ret_lobby[i][0] = self.conns[i].getIP()
            ret_lobby[i][1] = self.conns[i].getName()
        return ret_lobby
    
    def addConn(self, new_conn):
        self.conns.append(new_conn)

class Conn():
    def __init__(self, c_ip, c_name):
        self.conn_ip = c_ip
        self.conn_name = c_name
    
    def getIP(self):
        return self.conn_ip
    
    def getName(self):
        return self.conn_name

#------------------------------New Networked Game Functions------------------------------ 
def CreateLobby():
    lobby = Lobby()
    new_host = socket.gethostname()
    new_ip = socket.gethostbyname(new_host)
    new_conn = Conn(new_ip, new_host)
    lobby.addConn(new_conn)

    return lobby

#------------------------------New Networked Game Method------------------------------ 
def NewNet(mode, screen, clock):
    font_48 = pygame.font.SysFont('Arial', 48)
    
    if mode == "Host":
        lobby = CreateLobby()
        ip_text = font_48.render("Your IP: " + socket.gethostbyname(socket.gethostname()), True, (0,0,0))
        host_text = font_48.render("Host Name: " + socket.gethostname(), True, (0,0,0))

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

        if mode == "Host":
            screen.blit(ip_text, [10, 10])
            screen.blit(host_text, [10, 60])

        clock.tick(10) #10 fps
        pygame.display.flip() #Refresh screen

    return gotoScreen