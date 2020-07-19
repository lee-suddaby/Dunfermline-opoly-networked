import pygame
from pygame.locals import *
from copy import copy #Used when swapping and copy objects in arrays (e.g. the 2D array quicksort algorithm)
import numpy as np

from cls_net import *
from button import Button
from offline_lib import displayButtonRect
from msgbox import MessageBox

#------------------------------Leaderboards Functions------------------------------
#Create a 2D array to store the leaderboards data
#One column for player numbers, one for total money, one for assets value (includes money) and one for obtainable money (also includes the player's money)
def setup2DArray(netGame):
    no_of_players = netGame.countActivePlayers()
    ret_2D = np.zeros((no_of_players, 4), int)
    arr_count = 0
    for counter in range(no_of_players):
        if netGame.getPlayer(counter).player_active: 
            ret_2D[arr_count][0] = counter
            ret_2D[arr_count][1] = netGame.playerGetMoney(counter)
            ret_2D[arr_count][2] = netGame.getAssetsVal(counter)
            ret_2D[arr_count][3] = netGame.playerGetMoney(counter) + netGame.getObtainMon(counter)
            arr_count += 1
    return ret_2D

#Used for sorting the player data on a certain column in the 2D array (one column for each comparable attribute)
#asc is a boolean storing whether the array is being sorted ascending or descending (True for ascending, False for descending)
def quickSort(sort_arr, first, last, sort_col, asc):
    low = first
    high = last
    midValue = sort_arr[int((first+last)/2)][sort_col] #Middle item in the array

    while low <= high:
        if asc:
            while sort_arr[low][sort_col] < midValue:
                low += 1
            while sort_arr[high][sort_col] > midValue:
                high -= 1
        else:
            while sort_arr[low][sort_col] > midValue:
                low += 1
            while sort_arr[high][sort_col] < midValue:
                high -= 1

        if low <= high:
            sort_arr[low], sort_arr[high] = copy(sort_arr[high]), copy(sort_arr[low]) #Swap the two rows
            #copy is used here as otherwise, python does not actually copy the data, rather just pointers which mean the array ends up unsorted and with duplicated rows, despite a perfectly working algorithm
            low += 1
            high -= 1

    if first < high:
        sort_arr = quickSort(sort_arr, first, high, sort_col, asc) #Recursively call function, with differing partitions on the array

    if low < last:
        sort_arr = quickSort(sort_arr, low, last, sort_col, asc) #Recursively call function, with differing partitions on the array

    return sort_arr #Pass the array back out to where it was called, ending this level of recursion


#------------------------------Leaderboards Method------------------------------
def NetworkLeaderboards(netGame, screen, clock):
    font_48 = pygame.font.SysFont('Arial', 48) #Font for title and name
    font_40 = pygame.font.SysFont('Arial', 40) #Font for the "?" and Exit buttons
    font_28 = pygame.font.SysFont('Arial', 28) #Font for actual leaderboards and attributes
    font_32b = pygame.font.SysFont('Arial', 32, True) #Font for column headings

    lead_arr = setup2DArray(netGame)

    #Arrow images to be displayed on the buttons that are used by the player for choosing which column to sort on and whether to sort ascending or descending
    arrow_both = pygame.image.load("img/Arrows/both.png")
    arrow_up = pygame.image.load("img/Arrows/up.png")
    arrow_down = pygame.image.load("img/Arrows/down.png")
    
    #Initialise button array
    sort_buts = [pygame.Rect(360,80,40,40), pygame.Rect(610,80,40,40), pygame.Rect(940,80,40,40)]

    leader_buts = [Button(880, 10, 120, 50, 'Exit', font_40),
                   Button(819, 10, 50, 50, '?', font_40)]

    msgBox = MessageBox(screen, 'Total Money measures simply how much money each player has in the Bank. \n Total Assets counts the values of all owned properties, upgrades, etc. based on how much was paid for them initially. \n Obtainable Money is how much money each player could get if they were to sell off all of their properties and the like.', 'Leaderboards: Explained')
    msgBox.should_exit = True
    
    tit_text = font_48.render('Viewing Leaderboards:', True, (0,0,0)) #Render title at top left of screen
    head_1 = font_32b.render('Player', True, (0,0,0))
    head_2 = font_32b.render('Total Money', True, (0,0,0))
    head_3 = font_32b.render('Total Assets', True, (0,0,0))
    head_4 = font_32b.render('Obtainable Money', True, (0,0,0))
    mon_text = font_48.render(netGame.playerGetName(netGame.getCurPlayerNum()), True, (0,0,0)) #Render player money on screen
    f_width, f_height = font_48.size(netGame.playerGetName(netGame.getCurPlayerNum()))

    y_top = 120 #First y co-ordinate for a row of details
    y_space = 40 #Co-ordinate spacing between rows
    
    fps = 10
    sort_column = 1
    sort_asc = False
    sort_but_click = -1
    lead_arr = quickSort(lead_arr, 0, lead_arr.shape[0]-1, sort_column, sort_asc)
    leaderboards_running = True
    while leaderboards_running: #Main loop for this part of the program
        for event in pygame.event.get():
            for but in leader_buts:
                but.handle_input_event(event)

            msgBox.handle_input_event(event)
            if msgBox.should_exit == False:
                break
            if event.type == pygame.QUIT:
                leaderboards_running = False
                gotoScreen = -1
            if event.type == pygame.KEYDOWN: #If any key pressed
                if event.key == pygame.K_ESCAPE: #Escape key exits the game
                    leaderboards_running = False
                    gotoScreen = -1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #Left mouse button
                    mouse_pos = event.pos #Position of the cursor when nouse was clicked
                    for counter in range(3): #Cycle through all the arrays of buttons to see if any have been clicked
                        if sort_buts[counter].collidepoint(mouse_pos):
                            sort_but_click = counter

        screen.fill((255,255,255))
        screen.blit(tit_text, [10, 10])
        screen.blit(mon_text, [(770-f_width), 10])
        pygame.draw.rect(screen, (0,0,0), pygame.Rect(10,70,1000,700), 10) #Draw black rectangle surrounding the property data

        #Display each of the column headings (bold text)
        screen.blit(head_1, [30, 80])
        screen.blit(head_2, [200, 80])
        screen.blit(head_3, [450, 80])
        screen.blit(head_4, [700, 80])

        for counter in range(3):
            displayButtonRect(screen, sort_buts[counter], (100, 100, 100), font_28, '', (0, 0, 0))

            if counter == sort_column-1:
                if sort_asc:
                    screen.blit(arrow_down, [sort_buts[counter].x, sort_buts[counter].y])
                else:
                    screen.blit(arrow_up, [sort_buts[counter].x, sort_buts[counter].y])
            else:
                screen.blit(arrow_both, [sort_buts[counter].x, sort_buts[counter].y])

        y_pos = y_top #Y co-ordinate of the first row of data
        for counter in range(lead_arr.shape[0]):
            text_1 = font_28.render(mainGame.playerGetName(lead_arr[counter][0]), True, (0,0,0)) #Property name/title
            screen.blit(text_1, [30, y_pos])
            text_2 = font_28.render(str(lead_arr[counter][1]), True, (0,0,0)) 
            screen.blit(text_2, [200, y_pos])
            text_3 = font_28.render(str(lead_arr[counter][2]), True, (0,0,0)) 
            screen.blit(text_3, [450, y_pos])
            text_4 = font_28.render(str(lead_arr[counter][3]), True, (0,0,0))
            screen.blit(text_4, [700, y_pos])

            y_pos += y_space #Increment y co-ordinate variable by the difference in co-ordinates between each row, as already defined

        if sort_but_click != -1:
            if sort_column == sort_but_click+1:
                sort_asc = not sort_asc
            else:
                sort_column = sort_but_click + 1
                sort_asc = False

            lead_arr = quickSort(lead_arr, 0, lead_arr.shape[0]-1, sort_column, sort_asc)

        if leader_buts[0].clicked():
            leaderboards_running = False
            gotoScreen = 1

        if leader_buts[1].clicked():
            msgBox.should_exit = False

        msgBox.update()
        if msgBox.should_exit == False:
            msgBox.draw(screen)

        for but in leader_buts:
            but.render(screen)

        sort_but_click = -1
        clock.tick(fps) #10 fps currently, but could easily be changed to update more or less often
        pygame.display.flip() #Refresh display from a pygame perspective, to reflect the screen.blit()s
    return netGame, gotoScreen #Pass the Game object and the integer storing where the game will go to next back out to the main game loop
