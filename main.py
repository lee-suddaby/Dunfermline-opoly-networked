import pygame #Used for the creation of the GUI
import os #Used for creating directories
import ctypes #For getting screen dimensions

from cls_offline import * #All game classes
from cls_net import *

from offline_details import OfflinePropDetails
from offline_leaderboard import OfflineLeaderboards
from offline_maingame import OfflineMainScreen
from offline_pause import OfflinePauseMenu

from loading import LoadScreen
from new import NewGame
from newonoff import NewOnOff
from newnet import NewNet

#------------------------------Main Game Loop------------------------------
clock = pygame.time.Clock()
LoadScreen(clock)
nextScreen = NewOnOff(clock)

user32 = ctypes.windll.user32
screen_w = user32.GetSystemMetrics(0)
screen_h = user32.GetSystemMetrics(1)
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % ((screen_w - 1024)/2,(screen_h - 768)/2)

screen = pygame.display.set_mode([1024,768]) #Create screen in fullscreen mode and fill white
pygame.display.set_caption('Dunfermline-opoly')
screen.fill((255,255,255))

"""pygame.mixer.music.load('music.mp3') #Load in and set background music to play endlessly
pygame.mixer.music.play(-1)""" #Turned off while I'm developing this. Perhaps indefinitely if it turns out to be annoying enough.

mGame = None #Create blank object that will store the Game object
while nextScreen != -1: #Main Game Loop
    if nextScreen == 0: #New Game Screen
        mGame, nextScreen = NewGame(screen, clock)
    elif nextScreen == 1: #Main Game Screen
        mGame, nextScreen = OfflineMainScreen(mGame, screen, clock)
    elif nextScreen == 2: #Property Details Screen
        mGame, nextScreen = OfflinePropDetails(mGame, screen, clock)
    elif nextScreen == 3: #Leaderboards Screen
        mGame, nextScreen = OfflineLeaderboards(mGame, screen, clock)
    elif nextScreen == 4: #Pause Menu
        mGame, nextScreen = OfflinePauseMenu(mGame, screen, clock)
    elif nextScreen == 5: #Menu for starting a multiplayer game, currently in development
        nextScreen = NewNet(screen, clock)
    
pygame.quit() #Quits the pygame module and hence the GUI
