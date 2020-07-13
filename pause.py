import pygame
from pygame.locals import *
import os

from textbox import TextBox
from msgbox import MessageBox
from cls import *
from button import Button

#------------------------------Pause Menu Method------------------------------ 
def PauseMenu(mainGame, screen, clock):
    save_file_box = TextBox((340, 300, 560, 50), clear_on_enter=False, inactive_on_enter=False, active=False, active_color=pygame.Color("red")) #Create text box for storing save file path
    save_file_box.buffer = list(mainGame.save_path) #list() is used to convert string into array of characters

    music_box = pygame.Rect(100,200,40,40)
    font_48 = pygame.font.SysFont('Arial', 48) #Fonts used for texts, of various sizings
    font_60 = pygame.font.SysFont('Arial', 60)
    font_40 = pygame.font.SysFont('Arial', 40)
    font_28 = pygame.font.SysFont('Arial', 28)

    enable_txt = "Enable"
    if mainGame.autosave:
        enable_txt = "Disable"

    pause_buts = [Button(150, 425, 300, 80, "Save and Exit", font_40),
                  Button(600, 425, 300, 80, "Exit Without Saving", font_40),
                  Button(75, 620, 400, 80, "Save and Restart", font_40),
                  Button(550, 620, 400, 80, "Restart Without Saving", font_40),
                  Button(750, 10, 200, 80, "Resume", font_60),
                  Button(910, 300, 90, 50, "Change", font_28),
                  Button(910, 360, 90, 50, enable_txt, font_28)]

    msgBox = None #Will become MessageBox object as required
    
    pause_title = font_60.render("The Game is Paused", True, (0,0,0)) #Generate text for titles
    settings_txt = font_60.render("Settings:", True, (0,0,0)) #Settings sub-heading
    toggle_txt = font_48.render("Toggle Background Music", True, (0,0,0)) #Text next to check box
    save_txt = font_60.render("Save Game:", True, (0,0,0)) #Save Game sub-heading
    save_file_txt = font_48.render("Save File Path:", True, (0,0,0)) #Title of save path text box
    new_txt = font_60.render("New Game:", True, (0,0,0)) #New game sub-heading
    autosave_txt = [font_48.render("Autosave is currently off", True, (0,0,0)),font_48.render("Autosave is currently on", True, (0,0,0))]
                 
    music_box_click = False
    pause_menu_running = True
    while pause_menu_running:
        for event in pygame.event.get():
            for but in pause_buts:
                but.handle_input_event(event)
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
                    if music_box.collidepoint(event.pos): #Check box for toggling background music
                        music_box_click = True 
            save_file_box.get_event(event) #Function that allows each textbox to register key presses and the like

        screen.fill((255,255,255)) #Clear the screen
        pygame.draw.rect(screen, (0,0,0), pygame.Rect(50,20,20,60)) #Rectangles for pause symbol
        pygame.draw.rect(screen, (0,0,0), pygame.Rect(80,20,20,60))
        screen.blit(pause_title, [120, 10])
        screen.blit(settings_txt, [10, 110])

        pygame.draw.rect(screen, (0,0,0), music_box, 2) #Display blank check box
        if not mainGame.pause: #If music is unpaused, check box needs to be checked
            pygame.draw.line(screen, (0,0,0), [102, 220], [115, 238], 4) #Display two lines corresponding to the two parts of a tick
            pygame.draw.line(screen, (0,0,0), [115, 238], [145, 195], 4)

        screen.blit(toggle_txt, [150, 190])
        screen.blit(save_txt, [10, 240])
        screen.blit(save_file_txt, [30, 300])
        screen.blit(new_txt, [10, 550])

        save_file_box.update() #Update the textbox based on events
        save_file_box.draw(screen) #Draw the text box and contents on screen

        screen.blit(autosave_txt[int(mainGame.autosave)], [30, 360])

        if pause_buts[5].clicked(): #Button for updating save file path
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

        if pause_buts[6].clicked(): #Button for toggling autosave feature on/off
            mainGame.autosave = not mainGame.autosave #Toggle the boolean value of autosave
            if mainGame.autosave:
                pause_buts[6].updateCap("Disable")
            else:
                pause_buts[6].updateCap("Enable")

        if pause_buts[0].clicked(): #Save and Exit
            mainGame.saveGame() #Save game
            pause_menu_running = False #This screen no longer running
            gotoScreen = -1 #Don't go to any other screen (i.e. exit completely)

        if pause_buts[1].clicked(): #Exit without saving
            pause_menu_running = False #This screen no longer running
            gotoScreen = -1 #Don't go to any other screen (i.e. exit completely)

        if pause_buts[2].clicked(): #Save and restart
            mainGame.saveGame() #Save the game
            pause_menu_running = False #This screen no longer running
            gotoScreen = 0

        if pause_buts[3].clicked(): #Restart without saving
            pause_menu_running = False #This screen no longer running
            gotoScreen = 0 #Goto new game screen

        if pause_buts[4].clicked(): #Resume
            pause_menu_running = False
            gotoScreen = 1

        if music_box_click: #Check box for background music
            if mainGame.pause: #Music is currently paused
                pygame.mixer.music.unpause() #Unpause music
            else: #Music is currently unpaused
                pygame.mixer.music.pause() #Pause music
            mainGame.pause = not mainGame.pause #Toggle state of pause in Game class
         
        if msgBox != None: #If a MessageBox has been created
            msgBox.update() #Update message box with relevant events
            if msgBox.should_exit == False: #If message box should be showing
                msgBox.draw(screen) #Draw message box on screen

        for but in pause_buts:
            but.render(screen)

        music_box_click = False 
        clock.tick(10) #10 fps
        pygame.display.flip() #Refresh screen

    return mainGame, gotoScreen #Pass the Game object and the integer storing where the game will go to next back out to the main game loop
       