import pygame
from pygame.locals import *
import numpy as np
import random
import os
import ctypes #For getting screen dimensions

from anigif import AnimatedGif
from button import Button
from lib import getFileLines

#------------------------------Loading Screen functions------------------------------ 
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


#------------------------------Loading Screen Code------------------------------   
def LoadScreen(clock):   
    #Initialise pygame
    pygame.init()

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
    play_but = Button((width-200)/2, (850-height)/2, 200, 80, "Play", pygame.font.SysFont('Arial', 48))

    user32 = ctypes.windll.user32
    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % ((screen_w - width)/2,(screen_h - height)/2)

    screen = pygame.display.set_mode([width,height], pygame.NOFRAME)
    screen.fill((0,0,0))

    running = True
    tip_counter = 0 #Counts how many frames the current tip has been displayed for
    while running:
        for event in pygame.event.get():
            play_but.handle_input_event(event)
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: #If escape key is pressed
                    running = False #Game exists completely
                    pygame.quit() 

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
        play_but.render(screen)
        
        if play_but.clicked():
            running = False

        tip_counter = tip_counter + 1
        clock.tick(10)
        pygame.display.flip() #Update display