import pygame
from pygame.locals import *
import numpy as np

from msgbox import MessageBox
from lib import getObtainMon, displayButtonRect
from cls import *
from button import Button

#------------------------------Main Game Functions------------------------------
#Create the thumbnails showing all the properties on the board
#highlighting all the ones owned by a certain player
#Graphic returned is always the same size; its size on screen must be chosen when it is actually displayed if it needs to be different
def CreateThumbs(board, player):
    colour_on = pygame.Color(0,0,0)
    t_width = 45
    t_height = 70
    colour_counter = 0
    groups_done = 0
    specials = 0 #schools and stations
    
    thumbnails = pygame.Surface((450,200)) #Create new surface on which to blit title deed thumbnails as they are generated
    thumbnails.fill((255,255,255)) #Screen starts white
    
    for counter in range(board.max_pos+1): #For each property
        if board.getProp(counter).prop_type == Prop_Type.NORMAL: #Most common property, so one with a 'normal' title deed
            if board.getProp(counter).group_col != colour_on: #If we have reached a new group, reset the counter and note the new current group colour
                colour_on = board.getProp(counter).group_col #Set new current group colour
                colour_counter = 0 #Reset colour
                groups_done = groups_done + 1 #New group, so that's another one completed
            else: #Still on the same property group
                colour_counter = colour_counter + 1 #Increment counter

            #Create thumbnail using separate function
            #Second argument is a condition which evaluates to a boolean, hence becoming the value of this actual parameter passed into the CreatePropThumb function
            cur_thumb = CreatePropThumb(board.getProp(counter).group_col, board.getProp(counter).prop_owner == player) 
            #Complicated mathematical calculations to determine the exact position of the current thumbnail.
            #If in the same group, there is 5 pixels of movement to the right for each property, and vertical movement is one third of each thumbnails's height
            thumbnails.blit(cur_thumb, [(groups_done-1)*(t_width+int(t_width/5)) + colour_counter*int(t_width/5), colour_counter*int(t_height/3)])
        elif board.getProp(counter).prop_type == Prop_Type.SCHOOL or board.getProp(counter).prop_type == Prop_Type.STATION: #School and station properties
            specials = specials + 1
            cur_thumb = CreateThumbImg("img/Thumbs/" + board.getProp(counter).prop_title + ".png", board.getProp(counter).prop_owner == player)
            thumbnails.blit(cur_thumb, [(specials-1)*t_width + (specials-1)*int(t_width/5), 120]) #All these thumbnails are displayed in one horizontal line; therefore the same y-coordinate each time
    return thumbnails #pygame.Surface object that can be displayed on the screen as an image
            #441 x117

#Create an individual thumbnail to become a part of the method above (CreateThumbs)
#Only applicable for 'normal' properties; those that have images used the similar CreateThumbImg method
def CreatePropThumb(colour, bought):
    thumb = pygame.Surface((45,70))
    thumb.fill((255,255,255))

    outline = pygame.Rect(0,0,45,70)
    pygame.draw.rect(thumb, (0,0,0), outline, 1) #Thin black border outlining the entire title deed thumbnail

    top_rect = pygame.Rect(1,1,43,20)
    pygame.draw.rect(thumb, colour, top_rect) #Top of the title deed, where colour represents the property group

    #Black lines representing what would be text on the full size title deeds
    for counter in range(4):
        pygame.draw.line(thumb, (0,0,0), [5, counter*10 + 28], [40, counter*10 + 28], 4)

    if not bought: #Semi-transparent white overlay that makes the thumbnail look greyed out, compared to the fully coloured thumbnail if the property is owned
        overlay = pygame.Surface((45,70), pygame.SRCALPHA) #pygame.SRCALPHA allows the creation of a semi-transparent image
        overlay.fill((255,255,255,196)) #White overlay created here. 196 is the 'alpha' value, where 0 is full transparency and 255 is fully opaque
        thumb.blit(overlay, (0,0))
    return thumb #returns a pygame.Surface (i.e. pygame image)

#Creates thumbnail for school and station type properties, since they have an image (insiginia) on their title deeds
def CreateThumbImg(img_path, bought):
    thumb = pygame.Surface((45,70))
    thumb.fill((255,255,255))

    outline = pygame.Rect(0,0,45,70)
    pygame.draw.rect(thumb, (0,0,0), outline, 1) #Black border for the deed

    deed_img = pygame.transform.smoothscale(pygame.image.load(img_path), [35, 40]) #Load deed image (school crest or station logo)
    thumb.blit(deed_img, [5,3]) #Display so this it is horizontally centred

    pygame.draw.line(thumb, (0,0,0), [5, 50], [40, 50], 4) #Create black lines as would appear on the fully sized deed
    pygame.draw.line(thumb, (0,0,0), [5, 60], [40, 60], 4)

    if not bought: #Semi-transparent white overlay that makes the thumbnail look greyed out, compared to the fully coloured thumbnail if the property is owned
        overlay = pygame.Surface((45,70), pygame.SRCALPHA)
        overlay.fill((255,255,255,196))
        thumb.blit(overlay, (0,0))
    return thumb

def displayPropThumbs(screen, thumbs, x_pos, y_pos):
    screen.blit(thumbs, [x_pos, y_pos])

#Fill the screen white and show the game board
def displayScreenAndBoard(screen, board_img):
    screen.fill((255,255,255))
    screen.blit(board_img, [0,0])

#Show text displaying the number of the current player
def displayWhoseTurn(screen, font, player):
    turn_text = font.render(player.player_name, True, (0,0,0))
    screen.blit(turn_text, (650, 10))

#Render text showing how much money the current player has on screen
def displayPlayerMoney(screen, font, player_money):
    turn_text = font.render('£' + str(player_money), True, (0,0,0))
    f_width, f_height = font.size('£' + str(player_money))
    screen.blit(turn_text, (1000-f_width, 10))

#Display the token (i.e. the thing that moves around the board for the current player)
def displayPlayerToken(screen, player):
    screen.blit(pygame.transform.smoothscale(player.player_piece.piece_img, [50,50]), [600, 0])

#Display the graphic for, and number owned, of the available Council House and Tower Block upgrades
def displayUpgrades(screen, ch_img, tb_img, prop, font):
    screen.blit(ch_img, [400, 615]) #Display Council House graphic on screen
    screen.blit(tb_img, [570, 610]) #Display Tower Block graphic on screen
    ch_num = font.render(str(prop.C_Houses), True, (0,0,0)) #Generate and display the numbers of each of the upgardes horizontally next to the graphics
    tb_num = font.render(str(prop.T_Blocks), True, (0,0,0))
    screen.blit(ch_num, [360, 630])
    screen.blit(tb_num, [530, 630])

#For an owned property, display the player (Player 1, etc.) that actually is the owner
def displayOwner(screen, font, prop_owner):
    own_text = font.render('Owned By: ' + prop_owner.player_name, True, (0,0,0)) #+1 because first player is indexed zero, and humans don't start counting at zero.
    f_width, f_height = font.size('Owned By: ' + prop_owner.player_name)
    screen.blit(own_text, ((400-f_width)/2 + 600, 630))

#Display a properties rent from the point of view of it having been paid
def displayPaidRent(screen, font, rent):
    rent_text = font.render('You Paid £' + str(rent), True, (0,0,0))
    f_width, f_height = font.size('You Paid £' + str(rent))
    screen.blit(rent_text, ((400-f_width)/2 + 600, 660))
    
#Display a properties rent from its owner's perspecitve
def displayRent(screen, font, rent):
    rent_text = font.render('Current Rent - £' + str(rent), True, (0,0,0))
    f_width, f_height = font.size('Current Rent - £' + str(rent))
    screen.blit(rent_text, ((400-f_width)/2 + 600, 660))

#Display a Council Chest or Pot Luck card (only called if applicable)
def displayCard(screen, display_card):
    screen.blit(display_card.card_img, [635, 270])

#Render the texts describing the effects of the cards. Also returns the array of numerical values
def renderCardTexts(font, card):
    effs = card.card_nums #Obtain the numerical values for the effects
    texts = card.card_effects #Obtain the textual descriptors of the effects
    eff_count = 0 #Count how many effects are used in this card
    for counter in range(len(effs)):
        if int(effs[counter]) != -1: #-1 means not used
            eff_count += 1

    ret_texts = np.array([None] * eff_count) #Create final array, to later contain pygame text objects
    t_count = 0
    for counter in range(len(effs)):
        if int(effs[counter]) != -1:
            ret_texts[t_count] = font.render(texts[counter].replace("*", str(effs[counter])), True, (0,0,0)) #* is used where in the texts where it should be replaced with the number
            t_count += 1
    return effs, ret_texts

#Display the two images representing the scores on the two rolled dice
def displayDiceScore(screen, img_1, img_2):
    if img_1 != None and img_2 != None: #If there are actually images to display
        screen.blit(img_1, [185, 690])
        screen.blit(img_2, [255, 690])

#Display the tokens of every player on the relevant property on the board
def displayPieces(screen, gameObj):
    for counter in range(6):
        try:
            if gameObj.getPlayer(counter).player_active: #Only show the pieces of active players
                screen.blit(gameObj.getPlayer(counter).player_piece.piece_img, [gameObj.getPlayer(counter).player_piece.piece_x, gameObj.getPlayer(counter).player_piece.piece_y])
                if counter == gameObj.cur_player: #Draw red circle around the current player's token to highlight it to them
                    pygame.draw.circle(screen, (255,0,0), [int(gameObj.getPlayer(counter).player_piece.piece_x + 16), int(gameObj.getPlayer(counter).player_piece.piece_y + 16)], 20, 5)
        except IndexError: #If index does not exist in the game's Players array, no more players are left to show, thus the break
            break
                    

#------------------------------Main Game Code------------------------------         
def OfflineMainScreen(mainGame, screen, clock):
    mainGame.prop_thumbs = pygame.transform.smoothscale(CreateThumbs(mainGame.board, mainGame.cur_player), [385,170])

    roll_dice_button = pygame.Rect(180,610,150,70) #Create rectangle for roll dice/end turn button
    buy_prop_button = pygame.Rect(675,690,250,70) #Create rectangle for property buying button (also used for mortgaging and unmortgaging
    buy_upgrade_button = pygame.Rect(350,700,150,50)
    sell_upgrade_button = pygame.Rect(520,700,150,50)
    in_jail_button = pygame.Rect(350,610,150,70)

    TB_img = pygame.transform.smoothscale(pygame.image.load("img/Tower Block.png"), [75, 75])
    CH_img = pygame.transform.smoothscale(pygame.image.load("img/Council House.png"), [75, 75])
    
    font_40 = pygame.font.SysFont('Arial', 40) #Font object for button captions
    font_28 = pygame.font.SysFont('Arial', 28) #font object for displaying whose turn it is (among other things)
    font_20 = pygame.font.SysFont('Arial', 20) #Font for the upgrade buttons
    
    main_buts = [Button(10, 690, 150, 70, "Leaderboards", font_28),
               Button(10, 610, 150, 70, "Pause", font_40),
               Button(900, 160, 100, 50, "Details", font_28)]

    dice_but_click = False #Booleans tracking whether the roll dice, end turn and but property buttons have been clicked yet this turn
    turn_but_click = False
    buy_but_click = False
    mort_but_click = False
    buy_upgrade_but_click = False
    sell_upgrade_but_click = False
    leave_bogside_but_click = False
    use_card_but_click = False

    msgBox = None
    exitOnBoxClose = False
    advanceOnBoxClose = False
    fps = 10 #Used to determine the waiting between updating the game display

    main_screen_running = True
    while main_screen_running:
        for event in pygame.event.get():
            for but in main_buts:
                but.handle_input_event(event)

            if msgBox != None:
                msgBox.handle_input_event(event)
                if exitOnBoxClose and msgBox.should_exit:
                    main_screen_running = False
                    gotoScreen = -1
                if advanceOnBoxClose and msgBox.should_exit:
                    mainGame.advancePlayer()
                    mainGame.prop_thumbs = pygame.transform.smoothscale(CreateThumbs(mainGame.board, mainGame.cur_player), [385,170]) #Generate thumbnails for new player (here so it is only done when the player changes, not every frame change)
                    advanceOnBoxClose = False
                if msgBox.should_exit == False:
                    break
            if event.type == pygame.QUIT:
                main_screen_running = False
                gotoScreen = -1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: #Escape key exits the game
                    main_screen_running = False
                    gotoScreen = -1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #Left mouse button
                    mouse_pos = event.pos #Position of the cursor when nouse was clicked
                    if buy_prop_button.collidepoint(mouse_pos):
                        if mainGame.getCurProp().prop_owner == -1: #Property is unowned
                            buy_but_click = True
                        elif mainGame.getCurProp().prop_owner == mainGame.cur_player: #If owned by current player, it may be mortgaged
                            mort_but_click = True
                    if roll_dice_button.collidepoint(mouse_pos):
                        if mainGame.controller.card_used == False:
                            use_card_but_click = True #Roll dice button was clicked
                        elif mainGame.controller.player_rolled == False:
                            dice_but_click = True #End turn button was clicked
                        else:
                            turn_but_click = True #Button to apply card effects was clicked
                    if in_jail_button.collidepoint(mouse_pos): #Button to pay £50 to get out of bogside was clicked
                        leave_bogside_but_click = True
                    if buy_upgrade_button.collidepoint(mouse_pos):
                        buy_upgrade_but_click = True
                    if sell_upgrade_button.collidepoint(mouse_pos):
                        sell_upgrade_but_click = True
                    
                    
        #Clear screen and display main board
        displayScreenAndBoard(screen, mainGame.board.board_img)
        
        if dice_but_click: #If Roll Dice button was clicked
            #Roll dice, move the piece accordingly, and display the dice rolls
            mainGame.getDie(0).roll()
            mainGame.getDie(1).roll()

            dice_total = mainGame.getDiceTotal()
            
            if mainGame.getCurPlayer().player_inJail == False:
                mainGame.getCurPlayer().movePlayer(dice_total, mainGame.board)
            elif mainGame.getDie(0).cur_score == mainGame.getDie(1).cur_score: #Doubles rolled, so player gets out of bogside
                mainGame.getCurPlayer().leaveJail()
                mainGame.getCurPlayer().movePlayer(dice_total, mainGame.board)
            #Player does not move otherwise, as they must be lost in bogside

            #Generate the dice images
            mainGame.controller.roll_img1 = pygame.transform.smoothscale(mainGame.getDie(0).getImg(), [70, 70])
            mainGame.controller.roll_img2 = pygame.transform.smoothscale(mainGame.getDie(1).getImg(), [70, 70])

            if mainGame.getDie(0).cur_score != mainGame.getDie(1).cur_score: #If a double has not been rolled (rolling a double gives the player another turn)
                mainGame.controller.player_rolled = True #So player only gets another turn if they rolled doubles
            mainGame.controller.may_buy = True

            if mainGame.getDie(0).cur_score == mainGame.getDie(1).cur_score:
                mainGame.controller.cur_doubles += 1
                
            if mainGame.controller.cur_doubles >= 3: #If player rolls 3 consecutive doubles, they go to Bogside
                mainGame.sendCurPlayerToBog()
                mainGame.controller.player_rolled = True #Will not get to roll again
            
            #Determine rent if applicable
            mainGame.controller.turn_rent = mainGame.determineRent()

            if mainGame.controller.turn_rent != 0:
                mainGame.getCurPlayer().spendMoney(mainGame.controller.turn_rent) #Decrease the player's money and credit the owner of the property that amount
                if mainGame.getCurProp().prop_type != Prop_Type.PAYMENT:
                    mainGame.getPlayer(mainGame.getCurProp().prop_owner).addMoney(mainGame.controller.turn_rent)

            #If the current space returns a card
            if mainGame.getCurProp().prop_type == Prop_Type.POT_LUCK:
                mainGame.controller.cur_card = mainGame.board.PL_Deck.getNextCard()
            elif mainGame.getCurProp().prop_type == Prop_Type.COUNCIL_CHEST:
                mainGame.controller.cur_card = mainGame.board.CC_Deck.getNextCard()

            #If card will have just been returned, render the text that will show its effects
            if mainGame.getCurProp().prop_type == Prop_Type.POT_LUCK or mainGame.getCurProp().prop_type == Prop_Type.COUNCIL_CHEST: #Card will have been returned
                mainGame.controller.card_effs, mainGame.controller.card_texts = renderCardTexts(font_28, mainGame.controller.cur_card)
                mainGame.controller.card_used = False
                                
            #If the player lands on the 'Go To Bogside' space
            if mainGame.getCurProp().prop_type == Prop_Type.GO_TO_BOGSIDE:
                mainGame.sendCurPlayerToBog()

            
        #Display whose turn it is, how much money this player has, and show their property overview
        displayWhoseTurn(screen, font_28, mainGame.getCurPlayer())
        displayPlayerMoney(screen, font_28, mainGame.getCurPlayer().player_money)
        displayPlayerToken(screen, mainGame.getCurPlayer())
        displayPropThumbs(screen, mainGame.prop_thumbs, 610, 50)
        displayDiceScore(screen, mainGame.controller.roll_img1, mainGame.controller.roll_img2)
        
        #Show each of the player's pieces at its requisite position on the board
        displayPieces(screen, mainGame)

        #Show the Roll Dice/End Turn button, and the appropriate caption
        if mainGame.controller.card_used == False:
            displayButtonRect(screen, roll_dice_button, (100, 100, 100), font_40, 'Use Card', (0, 0, 0))
        elif mainGame.controller.player_rolled == False:
            displayButtonRect(screen, roll_dice_button, (100, 100, 100), font_40, 'Roll Dice', (0, 0, 0))
        else:
            displayButtonRect(screen, roll_dice_button, (100, 100, 100), font_40, 'End Turn', (0, 0, 0))

        if mainGame.getCurPlayer().player_inJail and mainGame.getCurPlayer().player_hasBogMap: #If player is lost in bogside, but they have the equivelant of a "Get out of Jail Free" card
            displayButtonRect(screen, in_jail_button, (100, 100, 100), font_28, 'Use Map', (0, 0, 0))
        elif mainGame.getCurPlayer().player_inJail: #Don't have card
            displayButtonRect(screen, in_jail_button, (100, 100, 100), font_28, 'Buy Map (£50)', (0, 0, 0))

        #Display title deed for property currently on
        if mainGame.getCurProp().prop_type == Prop_Type.NORMAL or mainGame.getCurProp().prop_type == Prop_Type.SCHOOL or mainGame.getCurProp().prop_type == Prop_Type.STATION: #If property actually will have a title deed to display
            title_deed = pygame.transform.smoothscale(mainGame.getCurProp().getTitleDeed(), [270,400])
            screen.blit(title_deed, [665, 230])

            if mainGame.getCurProp().prop_type == Prop_Type.NORMAL:
                #Normal properties are the only ones that can have Council Houses and Tower Blocks on them
                displayUpgrades(screen, CH_img, TB_img, mainGame.getCurProp(), font_40)

                if mainGame.getCurProp().prop_owner == mainGame.cur_player:
                    if mainGame.board.wholeGroupOwned(mainGame.cur_player, mainGame.getCurPlayer().player_pos): #May only be bought if the property is owned by the current player and the entire colour group is owned
                    
                        if mainGame.getCurProp().C_Houses < 4:
                            displayButtonRect(screen, buy_upgrade_button, (100, 100, 100), font_20, 'Buy Council House', (0, 0, 0))
                        elif mainGame.getCurProp().T_Blocks == 0:
                            displayButtonRect(screen, buy_upgrade_button, (100, 100, 100), font_20, 'Buy Tower Block', (0, 0, 0))

                        if mainGame.getCurProp().T_Blocks > 0:
                            displayButtonRect(screen, sell_upgrade_button, (100, 100, 100), font_20, 'Sell Tower Block', (0, 0, 0))
                        elif mainGame.getCurProp().C_Houses > 0:
                            displayButtonRect(screen, sell_upgrade_button, (100, 100, 100), font_20, 'Sell Council House', (0, 0, 0))
            
            if mainGame.getCurProp().prop_type == Prop_Type.NORMAL or mainGame.getCurProp().prop_type == Prop_Type.SCHOOL or mainGame.getCurProp().prop_type == Prop_Type.STATION:
                if mainGame.getCurProp().prop_owner == mainGame.cur_player:
                    #Display relevant button for mortgaging or unmortgaging a property
                    if mainGame.getCurProp().mortgage_status: #Property is mortgaged
                        displayButtonRect(screen, buy_prop_button, (100, 100, 100), font_28, 'Unmortgage Property', (0, 0, 0))
                    else:
                        displayButtonRect(screen, buy_prop_button, (100, 100, 100), font_28, 'Mortgage Property', (0, 0, 0))

            if mainGame.getCurProp().prop_owner == -1 and mainGame.controller.may_buy:
                #Give player the opportunity to buy property (since it is available and they have began their turn by rolling the dice)
                displayButtonRect(screen, buy_prop_button, (100, 100, 100), font_40, 'Buy Property', (0, 0, 0))
            elif mainGame.getCurProp().prop_owner != -1:
                #Property is owned by a player so display information pertaining to the owning of said property by this aforementioned player
                displayOwner(screen, font_28, mainGame.getPlayer(mainGame.getCurProp().prop_owner))
        else:
            if mainGame.getCurProp().prop_type != Prop_Type.LOST_IN_BOGSIDE: #Will work perfectly normally for all properties but the Lost In Bogside square
                tit_str = mainGame.getCurProp().prop_title
            elif mainGame.getCurPlayer().player_inJail: #If Player is actually 'in jail'
                tit_str = "Lost In Bogside"
            else:
                tit_str = "On The Paths" #In the same space but can move freely (i.e. 'not in jail')
                
            tit_text = font_40.render(tit_str, True, (0,0,0)) #Render the property name as it does not have a title deed that can do so
            t_width, t_height = font_40.size(tit_str)
            screen.blit(tit_text, [(400-t_width)/2 + 600, 220])

        if mainGame.getCurProp().prop_type == Prop_Type.NORMAL or mainGame.getCurProp().prop_type == Prop_Type.SCHOOL or mainGame.getCurProp().prop_type == Prop_Type.STATION or mainGame.getCurProp().prop_type == Prop_Type.PAYMENT: #If incurs a charge
            try:
                if mainGame.controller.turn_rent != 0: #If rent has actually been charged then the player is told they themselves have paid whatever amount
                    displayPaidRent(screen, font_28, mainGame.controller.turn_rent)
                elif mainGame.getCurProp().prop_owner == mainGame.cur_player and mainGame.getCurProp().prop_type == Prop_Type.NORMAL: #If property is owned by the current player and NORMAL (since other properties depend on those owned and dice rolls
                    if mainGame.board.wholeGroupOwned(mainGame.getCurProp().prop_owner, mainGame.getCurPlayer().player_pos) and mainGame.getCurProp().C_Houses == 0:
                        displayRent(screen, font_28, mainGame.getCurProp().getRent()*2)
                    else:
                        displayRent(screen, font_28, mainGame.getCurProp().getRent())
            except AttributeError: #Prevents errors as PAYMENT property has no owner but changes variable turn_rent
                pass
            
        if mainGame.getCurProp().prop_type == Prop_Type.POT_LUCK or mainGame.getCurProp().prop_type == Prop_Type.COUNCIL_CHEST:
            if mainGame.controller.cur_card != None: #If player was already on one of these places when their turn begins, cur_card and card_texts will be None object; this condition prevents an error when the following code thinks that it is
                displayCard(screen, mainGame.controller.cur_card)
                t_count = 0
                for cur_text in mainGame.controller.card_texts:
                    w, h = cur_text.get_size()
                    screen.blit(cur_text, [(400-w)/2 + 600, 480 + t_count*25])
                    t_count += 1
        
        if turn_but_click: #End Turn button
            #If player could sell some things to avoid going bankrupt
            cont = True
            if mainGame.getCurPlayer().player_money < 0 and (getObtainMon(mainGame.board, mainGame.cur_player) + mainGame.getCurPlayer().player_money) >= 0:
                msgBox = MessageBox(screen, 'You need to ensure your money is 0 or above before you can finish your turn. Please sell or mortgage some assets to continue.', 'Not Enough Money')
                cont = False
            elif (getObtainMon(mainGame.board, mainGame.cur_player) + mainGame.getCurPlayer().player_money) < 0: #If it is impossible for a player to not end up in debt, they go bankrupt
                mainGame.getCurPlayer().deactivate() #Remove player from the game
                cont = False
                for counter in range(mainGame.board.max_pos):
                    if mainGame.board.getProp(counter).prop_type == Prop_Type.NORMAL:
                        if mainGame.board.getProp(counter).prop_owner == mainGame.cur_player:
                            mainGame.board.getProp(counter).p_owner = -1
                            mainGame.board.getProp(counter).mortgage_status = False
                            mainGame.board.getProp(counter).C_Houses = 0
                            mainGame.board.getProp(counter).T_Blocks = 0
                    if mainGame.board.getProp(counter).prop_type == Prop_Type.SCHOOL or mainGame.board.getProp(counter).prop_type == Prop_Type.STATION:
                        if mainGame.board.getProp(counter).prop_owner == mainGame.cur_player:
                            mainGame.board.getProp(counter).p_owner = -1
                            mainGame.board.getProp(counter).mortgage_status = False
                        
                msgBox = MessageBox(screen, 'Unfortunately, this utopian capitalist world has ceased to be utopian for you: you have gone bankrupt and are no longer in the game.', 'Game Over')
                advanceOnBoxClose = True
                
            #Next player's turn now (if the previous player has no more to do
            if cont:
                mainGame.advancePlayer()
                mainGame.prop_thumbs = pygame.transform.smoothscale(CreateThumbs(mainGame.board, mainGame.cur_player), [385,170]) #Generate thumbnails for new player (here so it is only done when the player changes, not every frame change)

            if mainGame.countActivePlayers() < 2:
                mainGame.advancePlayer()
                msgBox = MessageBox(screen, mainGame.getCurPlayer().player_name + ' has won the game.', 'Game Over')
                exitOnBoxClose = True
            
        #Button for buying a property has been clicked
        if buy_but_click and (mainGame.getCurProp().prop_type == Prop_Type.NORMAL or mainGame.getCurProp().prop_type == Prop_Type.SCHOOL or mainGame.getCurProp().prop_type == Prop_Type.STATION): #Final check that the property can actually be owned
            #Player wished to buy property
            if mainGame.getCurProp().prop_owner == -1: #Property is unowned, hence can actually be bought
                if mainGame.getCurPlayer().player_money >=  mainGame.getCurProp().cost:
                    #Player has enough money
                    mainGame.getCurPlayer().spendMoney(mainGame.getCurProp().cost) #Decrease the player's bank balance accordingly
                    mainGame.getCurProp().buyProperty(mainGame.cur_player) #Change the property's status to track the new ownership
                    mainGame.prop_thumbs = pygame.transform.smoothscale(CreateThumbs(mainGame.board, mainGame.cur_player), [385,170]) #Update title deed thumbnails to reflect newly purchased properties
        
        #Button to apply the effects of a Pot Luck or Council Chest card
        if use_card_but_click and mainGame.controller.cur_card != None: #Check there is a card to work with
            mainGame.controller.card_used = True
            mainGame.applyCardEffects() #Apply card effects

        #All of the following may only be done if the current player owns the property
        #Button for mortgaging or unmortgaging a property
        if mort_but_click and (mainGame.getCurProp().prop_type == Prop_Type.NORMAL or mainGame.getCurProp().prop_type == Prop_Type.SCHOOL or mainGame.getCurProp().prop_type == Prop_Type.STATION): #Final check that the property is one that may be mortgaged
            if mainGame.getCurProp().prop_owner == mainGame.cur_player and mainGame.getCurProp().mortgage_status == False: #Property must be owned by the current player and not already mortgaged
                mainGame.getCurProp().mortgage_status = True #Property is now mortgaged
                mainGame.getCurPlayer().addMoney(int(mainGame.getCurProp().mortgage_val))
            elif mainGame.getCurProp().prop_owner == mainGame.cur_player and mainGame.getCurProp().mortgage_status: #Property must be owned by the current player and is mortgaged
                if mainGame.getCurPlayer().player_money >= mainGame.getCurProp().mortgage_val * 1.2: #Player has sufficient money to unmortgage the property (twice the money gotten by mortgaging it)
                    mainGame.getCurProp().mortgage_status = False #Property is no longer in a state of being mortgaged
                    mainGame.getCurPlayer().spendMoney(int(mainGame.getCurProp().mortgage_val * 1.2)) #Decrease player's money by the cost of unmortgaging the property
        
        #Button for buying a Council House or Tower Block
        if buy_upgrade_but_click and mainGame.getCurProp().prop_type == Prop_Type.NORMAL and mainGame.board.wholeGroupOwned(mainGame.cur_player, mainGame.getCurPlayer().player_pos): #Player wishes to upgrade the property and said upgrade can actually be purchaed
            if mainGame.getCurProp().prop_owner == mainGame.cur_player: #May only be bought if the property is owned by the current player     
                if mainGame.getCurProp().C_Houses < 4: #Fewer than 4  Council Houses, so these are the next upgrade to be bought 
                    if mainGame.getCurPlayer().player_money >= (mainGame.getCurProp().CH_cost * mainGame.board.countGroupSize(mainGame.cur_player, mainGame.getCurPlayer().player_pos)): #Player actually has enough money to buy the Council House upgrade
                        mainGame.board.buyCHGroup(mainGame.cur_player, mainGame.getCurPlayer().player_pos) #Buy the Council Houses for the whole group
                        mainGame.getCurPlayer().spendMoney(mainGame.getCurProp().CH_cost * mainGame.board.countGroupSize(mainGame.cur_player, mainGame.getCurPlayer().player_pos)) #Decrease the player's money by the cost of a Council House for however many properties are in the group
                elif mainGame.getCurProp().C_Houses == 4 and mainGame.getCurProp().T_Blocks == 0: #4 Council Houses and no Tower Blocks, so Tower Block can be bought 
                    if mainGame.getCurPlayer().player_money >= (mainGame.getCurProp().TB_cost * mainGame.board.countGroupSize(mainGame.cur_player, mainGame.getCurPlayer().player_pos)): #Player actually has enough money to buy the Tower Block upgrade
                        mainGame.board.buyTBGroup(mainGame.cur_player, mainGame.getCurPlayer().player_pos) #Buy the Council Houses for the whole group
                        mainGame.getCurPlayer().spendMoney(mainGame.getCurProp().TB_cost * mainGame.board.countGroupSize(mainGame.cur_player, mainGame.getCurPlayer().player_pos)) #Decrease the player's money by the cost of a Tower Block for however many properties are in the group

        #Button for selling a Council House or Tower Block
        if sell_upgrade_but_click and mainGame.getCurProp().prop_type == Prop_Type.NORMAL and mainGame.board.wholeGroupOwned(mainGame.cur_player, mainGame.getCurPlayer().player_pos): #Player wishes to upgrade the property and said upgrade can actually be purchaed
            if mainGame.getCurProp().prop_owner == mainGame.cur_player: #May only be bought if the property is owned by the current player     
                if mainGame.getCurProp().T_Blocks > 0: #Property has a Tower Block that can be sold
                    mainGame.board.sellTBGroup(mainGame.cur_player, mainGame.getCurPlayer().player_pos) #Sell the Tower Blocks for the whole group
                    mainGame.getCurPlayer().addMoney(int(mainGame.getCurProp().TB_cost/2 * mainGame.board.countGroupSize(mainGame.cur_player, mainGame.getCurPlayer().player_pos))) #Increase the player's money by half of what the upgrades were bought for
                elif mainGame.getCurProp().C_Houses > 0: #No Tower Blocks, buy some Council Houses which can instead be sold 
                    mainGame.board.sellCHGroup(mainGame.cur_player, mainGame.getCurPlayer().player_pos) #Sell the Council Houses for the whole group
                    mainGame.getCurPlayer().addMoney(int(mainGame.getCurProp().CH_cost/2 * mainGame.board.countGroupSize(mainGame.cur_player, mainGame.getCurPlayer().player_pos))) #Increase the player's money by half of what the upgrades were bought for

        #Button to buy a map out of Bogside for £50
        if leave_bogside_but_click and (mainGame.getCurPlayer().player_money >= 50 or mainGame.getCurPlayer().player_hasBogMap) and mainGame.getCurPlayer().player_inJail:
            mainGame.getCurPlayer().leaveJail()
            if mainGame.getCurPlayer().player_hasBogMap == False:
                mainGame.getCurPlayer().spendMoney(50)
            else:
                mainGame.getCurPlayer().useBogMap()

        if msgBox != None:
            msgBox.update()
            if msgBox.should_exit == False:
                msgBox.draw(screen)
        
        if main_buts[2].clicked(): #Details
            main_screen_running = False
            gotoScreen = 2
        if main_buts[0].clicked(): #Leaderboards
            main_screen_running = False
            gotoScreen = 3
        if main_buts[1].clicked(): #Pause
            main_screen_running = False
            gotoScreen = 4

        for but in main_buts:
            but.render(screen)

        #Reset button booleans so that effects of clicking buttons do not happen more than once
        dice_but_click = False
        turn_but_click = False
        buy_but_click = False
        mort_but_click = False
        buy_upgrade_but_click = False
        sell_upgrade_but_click = False
        leave_bogside_but_click = False
        use_card_but_click = False
        clock.tick(fps) #10 fps currently, but could easily be changed to update more or less often
        pygame.display.flip() #Refresh display from a pygame perspective, to reflect the screen.blit()s
    return mainGame, gotoScreen #Pass the Game object and the integer storing where the game will go to next back out to the main game loop
