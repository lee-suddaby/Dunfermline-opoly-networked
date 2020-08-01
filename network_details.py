import pygame
from pygame.locals import *
import numpy as np

from cls_net import *
from button import Button
from lib import displayButtonRect


#------------------------------Property Details Method------------------------------
def NetworkPropDetails(netGame, localGame, screen, clock):
    font_40 = pygame.font.SysFont('Arial', 40) #Font for title, money and exit button
    font_20 = pygame.font.SysFont('Arial', 20) #Font for actual property details
    font_20b = pygame.font.SysFont('Arial', 20, True) #Font for column headings
    font_16 = pygame.font.SysFont('Arial', 16) #Font for button captions

    board_poses = netGame.setupBoardPoses() #Array containing the board positions of all of the current player's owned properties
    props_owned = len(board_poses) #Number of properties owned by the player

    tit_text = font_40.render('Viewing Property Details:', True, (0,0,0)) #Render title at top left of screen

    headers = [font_20b.render('Property', True, (0,0,0)),
               font_20b.render('Group', True, (0,0,0)),
               font_20b.render('Rent (£)', True, (0,0,0)),
               font_20b.render('Mortgage(£)', True, (0,0,0)),
               font_20b.render('CH/TB', True, (0,0,0)),
               font_20b.render('Options', True, (0,0,0))]
    head_x = [30, 200, 260, 330, 440, 640]

    #Initialise button arrays
    buy_buts = np.array([None] * props_owned)
    sell_buts = np.array([None] * props_owned)
    mort_buts = np.array([None] * props_owned)
    deed_buts = np.array([None] * props_owned)
    exit_but = pygame.Rect(880,10,120,50)
    
    y_top = 90 #First y co-ordinate for a row of details
    y_space = 30 #Co-ordinate spacing between rows

    #Setup buttons (one element of each array for each property)
    for counter in range(props_owned):
        buy_buts[counter] = pygame.Rect(500, y_top + y_space*counter, 60, 25)
        sell_buts[counter] = pygame.Rect(565, y_top + y_space*counter, 60, 25)
        mort_buts[counter] = pygame.Rect(630, y_top + y_space*counter, 60, 25)
        deed_buts[counter] = pygame.Rect(695, y_top + y_space*counter, 75, 25)
    exit_but = Button(880, 10, 120, 50, "Exit", font_40)

    fps = 10
    cur_deed = None #Image for a title deed that is being displayed at any one moment
    deed_prop = -1 #Board position of the property whose title deed is currently being shown
    buy_but_click = -1  #Variables storing when buttons are clicked
    sell_but_click = -1 #-1 indicates not clicked for this iteration
    mort_but_click = -1 #Not -1 indicates the integer contents of the variable is the row of whatever of the four types of button was clicked (zero-indexed)
    deed_but_click = -1

    cur_player = netGame.getCurPlayerNum()
    prop_details_running = True
    while prop_details_running: #Main loop for this part of the program
        for event in pygame.event.get():
            exit_but.handle_input_event(event)
            if event.type == pygame.QUIT:
                prop_details_running = False
                gotoScreen = -1
            if event.type == pygame.KEYDOWN: #If any key pressed
                if event.key == pygame.K_ESCAPE: #Escape key exits the game
                    prop_details_running = False
                    gotoScreen = -1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #Left mouse button
                    mouse_pos = event.pos #Position of the cursor when nouse was clicked
                    for counter in range(props_owned): #Cycle through all the arrays of buttons ot see if any have been clicked
                        if buy_buts[counter].collidepoint(mouse_pos):
                            buy_but_click = counter
                        if sell_buts[counter].collidepoint(mouse_pos):
                            sell_but_click = counter
                        if mort_buts[counter].collidepoint(mouse_pos):
                            mort_but_click = counter
                        if deed_buts[counter].collidepoint(mouse_pos):
                            deed_but_click = counter

        screen.fill((255,255,255))
        
        screen.blit(tit_text, [10, 0])
        pygame.draw.rect(screen, (0,0,0), pygame.Rect(10,50,770,700), 10) #Draw black rectangle surrounding the property data

        player_mon = str(netGame.playerGetMoney(cur_player)) #(One of many) temp variables to cut down on network accesses
        mon_text = font_40.render('£' + player_mon, True, (0,0,0)) #Render player money on screen
        f_width, f_height = font_40.size('£' + player_mon)
        screen.blit(mon_text, [(770-f_width), 0])

        #Display each of the column headings
        for counter in range(6):
            screen.blit(headers[counter], [head_x[counter], 60])

        if cur_deed != None: #Can only display a chosen title deed if one has already been chosen
            screen.blit(cur_deed, [790, 200])

        y_pos = y_top #Y co-ordinate of the first row of data
        for counter in range(props_owned):
            cur_pos = board_poses[counter]

            text_1 = font_20.render(localGame.board.properties[cur_pos].prop_title, True, (0,0,0)) #Property name/title
            screen.blit(text_1, [30, y_pos])
            
            if localGame.board.properties[cur_pos].prop_type == Prop_Type.NORMAL: #SCHOOL and STATION properties have no 'Group Colour', Council Houses or Tower Blocks
                pygame.draw.rect(screen, localGame.board.properties[cur_pos].group_col, pygame.Rect(200,y_pos,30,20))

                show_rent = netGame.propertyGetRent(cur_pos)
                if netGame.boardWholeGroupOwned(netGame.getCurPlayerNum(), cur_pos) and netGame.propertyGetCH(cur_pos) == 0:
                    show_rent = show_rent * 2

                text_2 = font_20.render(str(show_rent), True, (0,0,0))
                screen.blit(text_2, [260, y_pos])
                text_4 = font_20.render(str(netGame.propertyGetCH(cur_pos)) + '/' + str(netGame.propertyGetTB(cur_pos)), True, (0,0,0))
                screen.blit(text_4, [440, y_pos])

            text_3 = font_20.render(str(netGame.propertyGetMortVal(cur_pos)), True, (0,0,0)) #Mortgage value of the property
            screen.blit(text_3, [330, y_pos])

            y_pos += y_space #Increment y co-ordinate variable by the difference in co-ordinates between each row, as already defined

            if netGame.boardWholeGroupOwned(netGame.getCurPlayerNum(), cur_pos):
                if netGame.propertyGetCH(cur_pos) < 4: #Council Houses are still available to buy
                    displayButtonRect(screen, buy_buts[counter], (100, 100, 100), font_16, 'Buy CH', (0, 0, 0))
                elif netGame.propertyGetTB(cur_pos) == 0: #Player may still buy a Tower Block
                    displayButtonRect(screen, buy_buts[counter], (100, 100, 100), font_16, 'Buy TB', (0, 0, 0))

                if netGame.propertyGetTB(cur_pos) > 0: #Player has Tower Blocks available to sell
                    displayButtonRect(screen, sell_buts[counter], (100, 100, 100), font_16, 'Sell TB', (0, 0, 0))
                elif netGame.propertyGetCH(cur_pos) > 0: #Player has no Tower Blocks, but still has Council Houses which may be sold
                    displayButtonRect(screen, sell_buts[counter], (100, 100, 100), font_16, 'Sell CH', (0, 0, 0))

            if netGame.propertyGetMortStat(cur_pos): #Properrty is mortgaged, thus it can only be bought back
                displayButtonRect(screen, mort_buts[counter], (100, 100, 100), font_16, 'Buy-Back', (0, 0, 0))
            else: #Property may be mortgaged as it is not currently mortgaged
                displayButtonRect(screen, mort_buts[counter], (100, 100, 100), font_16, 'Mortgage', (0, 0, 0))
   
            displayButtonRect(screen, deed_buts[counter], (100, 100, 100), font_16, 'View Deed', (0, 0, 0))

        if mort_but_click != -1: #One of the mortgaging buttons has been clicked
            cur_pos = board_poses[mort_but_click]
            if netGame.propertyGetMortStat(cur_pos) == False: #Unmortgaged
                netGame.propertySetMortStat(cur_pos, True) #Mortgage property
                netGame.playerAddMoney(netGame.propertyGetMortVal(cur_pos), netGame.getCurPlayerNum()) #Increase the player's money by the mortgage value of the property
            else: #Mortgaged already
                if netGame.playerGetMoney(cur_player) >= netGame.propertyGetMortVal(cur_pos) * 1.2: #If the player has 120% of the mortgage value of the property (this is the buy-back cost)
                    netGame.propertySetMortStat(cur_pos, False) #Unmortgage the property
                    netGame.playerSpendMoney(int(netGame.propertyGetMortVal(cur_pos) * 1.2), netGame.getCurPlayerNum()) #Debit the player's money by 120% of the mortgage value
            if deed_prop == cur_pos: #If title deed has changed 
                cur_deed = pygame.transform.smoothscale(localGame.board.getProp(cur_pos).getTitleDeed(netGame.propertyGetMortStat(cur_pos)), [225,400])

        if deed_but_click != -1: #One of the buttons for viewing a title deed has been clicked
            cur_pos = board_poses[deed_but_click]
            cur_deed = pygame.transform.smoothscale(localGame.board.getProp(cur_pos).getTitleDeed(netGame.propertyGetMortStat(cur_pos)), [225,400]) #Scale title deed so it fits in the narrow sidebar
            deed_prop = cur_pos

        if buy_but_click != -1: #One of the buttons for buying CH or TB has been clicked
            cur_pos = board_poses[buy_but_click]
            if netGame.propertyGetCH(cur_pos) < 4: #Fewer than 4  Council Houses, so these are the next upgrade to be bought 
                if netGame.playerGetMoney(cur_player) >= (netGame.propertyGetCHCost(cur_pos) * netGame.boardCountGroupSize(netGame.getCurPlayerNum(), cur_pos)): #Player actually has enough money to buy the Council House upgrade
                    netGame.boardBuyCHGroup(netGame.getCurPlayerNum(), cur_pos) #Buy the Council Houses for the whole group
                    netGame.playerSpendMoney(netGame.propertyGetCHCost(cur_pos) * netGame.boardCountGroupSize(netGame.getCurPlayerNum(), cur_pos), netGame.getCurPlayerNum()) #Decrease the player's money by the cost of a Council House for however many properties are in the group
            elif netGame.propertyGetCH(cur_pos) == 4 and netGame.propertyGetTB(cur_pos) == 0: #4 Council Houses and no Tower Blocks, so Tower Block can be bought 
                if netGame.playerGetMoney(cur_player) >= (netGame.propertyGetTBCost(cur_pos) * netGame.boardCountGroupSize(netGame.getCurPlayerNum(), cur_pos)): #Player actually has enough money to buy the Tower Block upgrade
                    netGame.boardBuyCHGroup(netGame.getCurPlayerNum(), cur_pos) #Buy the Council Houses for the whole group
                    netGame.playerSpendMoney(netGame.propertyGetTBCost(cur_pos) * netGame.boardCountGroupSize(netGame.getCurPlayerNum(), cur_pos), netGame.getCurPlayerNum()) #Decrease the player's money by the cost of a Tower Block for however many properties are in the group

        if sell_but_click != -1: #One of the buttons for selling CH or TB has been clicked
            cur_pos = board_poses[sell_but_click]
            if netGame.propertyGetTB(cur_pos) > 0: #Property has a Tower Block that can be sold
                netGame.boardSellTBGroup(netGame.getCurPlayerNum(), cur_pos) #Sell the Tower Blocks for the whole group
                add_mon = int(netGame.propertyGetTBCost(cur_pos)/2 * netGame.boardCountGroupSize(netGame.getCurPlayerNum(), cur_pos))
                netGame.playerAddMoney(add_mon, netGame.getCurPlayerNum()) #Increase the player's money by half of what the upgrades were bought for
            elif netGame.propertyGetCH(cur_pos) > 0: #No Tower Blocks, buy some Council Houses which can instead be sold 
                netGame.boardSellCHGroup(netGame.getCurPlayerNum(), cur_pos) #Sell the Council Houses for the whole group
                add_mon = int(netGame.propertyGetCHCost(cur_pos)/2 * netGame.boardCountGroupSize(netGame.getCurPlayerNum(), cur_pos))
                netGame.playerAddMoney(add_mon, netGame.getCurPlayerNum()) #Increase the player's money by half of what the upgrades were bought for
        
        if exit_but.clicked():
            prop_details_running = False
            gotoScreen = 6
        exit_but.render(screen)

        #Reset all button variables so the actions of buttons only happen once
        buy_but_click = -1
        sell_but_click = -1
        mort_but_click = -1
        deed_but_click = -1
        clock.tick(fps) #10 fps currently, but could easily be changed to update more or less often
        pygame.display.flip() #Refresh display from a pygame perspective, to reflect the screen.blit()s
    return netGame, localGame, gotoScreen #Pass the Game object and the integer storing where the game will go to next back out to the main game loop
