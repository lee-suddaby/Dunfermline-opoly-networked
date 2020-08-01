#Functions used in multiple screens, stored here to prevent duplication of code
from cls_offline import *

def dim(a): #Function to determine the dimensions of a python list
    if not type(a) == list:
        return []
    return [len(a)] + dim(a[0])
    
#Determine how many lines are in a text file
#Used when loading the tips file so the number of tips need not be counted
def getFileLines(filePath):
    with open(filePath) as fh:
        #enumerate is a python-specific function used to loop through all lines in the file and keep an incremental counter automatically, similar to a count occurrences algorithm, except here there is no condition to the counting
        #Slightly simply than manually incrementing a separate counter variable and keeping doing so until the end of the file is reached
        for i, l in enumerate(fh,1):
            pass
    return i

#Loads text file describing the effects of the Pot Luck and Council Chest cards, e.g. "Pay £*", where the * will be replaced with a number later
def getCardEffects(card_texts_path_eff):
    texts_num = getFileLines(card_texts_path_eff)
    card_effects = [None] * texts_num #None used so length of string is not limited
    fh = open(card_texts_path_eff, "r")
    for effects_counter in range(texts_num):
        card_effects[effects_counter] = fh.readline().strip()
    fh.close()
    return card_effects

#Determine how much money a player could obtain from selling/mortgaging all of their properties and upgrades
def getObtainMon(board, player_num):
    ret_val = 0

    for counter in range(board.max_pos + 1):
        if board.getProp(counter).prop_type == Prop_Type.NORMAL:
            if board.getProp(counter).prop_owner == player_num:
                ret_val += int(board.getProp(counter).CH_cost * board.getProp(counter).C_Houses / 2)
                ret_val += int(board.getProp(counter).TB_cost * board.getProp(counter).T_Blocks / 2)
                if board.getProp(counter).mortgage_status == False:
                    ret_val += board.getProp(counter).mortgage_val

        if board.getProp(counter).prop_type == Prop_Type.SCHOOL:
            if board.getProp(counter).prop_owner == player_num and board.getProp(counter).mortgage_status == False:
                    ret_val += board.getProp(counter).mortgage_val
    return ret_val

#Button drawing using a pygame.Rect object (which I also use for mouse click collision detection)
def displayButtonRect(screen, rect, but_col, font, caption, txt_col, enabled = True):
    pygame.draw.rect(screen, but_col, rect)

    f_width, f_height = font.size(caption)
    cap_text = font.render(caption, True, txt_col)
    screen.blit(cap_text, [(rect.width-f_width)/2 + rect.left,(rect.height-f_height)/2 + rect.top]) #Displays the text in the centre of the button - (button_width - text_width)/2

    if not enabled:
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((but_col[0], but_col[1], but_col[2], 196))
        screen.blit(overlay, [rect.left, rect.top])

#Render a title deed for a property (that can be mortgaged) for when it is actually mortgaged
#Only shows the name, buy-back cost and a mnessage explaining that the property needs to be rebought for it to collect rent again
def CreateMortDeed(deed_name, deed_cost):
    deed_screen = pygame.Surface((250,400))
    deed_screen.fill((255,255,255)) #Filled white

    deed_font_name = pygame.font.SysFont('Arial', 24, True) #Font for property name (bold)
    deed_font_desc = pygame.font.SysFont('Arial', 18) #Font for descriptive text that tells the user that the property will not collect rent while still mortgaged
    deed_font_back = pygame.font.SysFont('Arial', 28) #Font for displaying the cost to unmortgage/buy-back the property

    pygame.draw.rect(deed_screen, (0,0,0), pygame.Rect(0,0,250,400), 2) #Title deed outline

    prop_text = deed_font_name.render(deed_name, True, (0,0,0)) #Name of property (in bold) at the top of the deed
    f_width, f_height = deed_font_name.size(deed_name) #Used repeatedly so that text can be centred, using the equation (xpos = (deed_width-text_width)/2)
    deed_screen.blit(prop_text, [(250-f_width)/2, 80])

    desc_text_1 = deed_font_desc.render('This property is currently mortgaged.', True, (0,0,0)) #First line of the deed description
    f_width, f_height = deed_font_desc.size('This property is currently mortgaged.')
    deed_screen.blit(desc_text_1, [(250-f_width)/2, 140])

    desc_text_2 = deed_font_desc.render('It will not collect rent until bought back.', True, (0,0,0)) #Second line of the deed description
    f_width, f_height = deed_font_desc.size('It will not collect rent until bought back.')
    deed_screen.blit(desc_text_2, [(250-f_width)/2, 158])

    buy_back_text = deed_font_back.render('Buy-Back Cost £' + str(int(deed_cost)), True, (0,0,0)) #Text displaying how much it costs to unmortgage the property
    f_width, f_height = deed_font_back.size('Buy-Back Cost £' + str(int(deed_cost)))
    deed_screen.blit(buy_back_text, [(250-f_width)/2, 275])
    
    return deed_screen

#Render a title deed for a typical property based on its rents, cost,
#etc Returns a pygame Surface containing shapes and text resembling a
#title deed
def CreateTitleDeed(deed_vals):
    deed_screen = pygame.Surface((225,400))
    deed_screen.fill((255,255,255)) #Filled white

    deed_col = pygame.Color(int(deed_vals[11]), int(deed_vals[12]), int(deed_vals[13]), 0) #Create colour to be used in header from the 3 separate RGB values
    #Create fonts for title deed
    deed_font_main = pygame.font.SysFont('Arial', 18) #Font for most text
    deed_font_name = pygame.font.SysFont('Arial', 20, True) #Bold font holding the name of the property
    deed_font_bottom = pygame.font.SysFont('Arial', 14) #Font for displaying the info at the bottom of the property about rent doubling if all properties in the gropup are owned

    pygame.draw.rect(deed_screen, (0,0,0), pygame.Rect(0,0,225,400), 2) #Title deed outline
    pygame.draw.rect(deed_screen, deed_col, pygame.Rect(5, 5, 215, 100)) #Coloured rectangle containing the words 'Title Deed' and property name
    
    prop_text = deed_font_name.render(deed_vals[0], True, (255,255,255)) #Name of property (in bold) at bottom of above coloured rectangle
    f_width, f_height = deed_font_name.size(deed_vals[0]) #Used repeatedly so that text can be centred, using the equation (xpos = (deed_width-text_width)/2)
    deed_screen.blit(prop_text, [(225-f_width)/2, 95 - f_height])

    title_text = deed_font_main.render('Title Deed', True, (255,255,255)) #Words 'Title Deed' at the top of the aforementioned coloured rectangle
    f_width, f_height = deed_font_main.size('Title Deed')
    deed_screen.blit(title_text, [(225-f_width)/2, 5])

    cost_text = deed_font_main.render('Cost £' + str(deed_vals[1]), True, (0,0,0)) #The cost to buy the property from the bank
    f_width, f_height = deed_font_main.size('Cost £' + str(deed_vals[1]))
    deed_screen.blit(cost_text, [(225-f_width)/2, 105])
    
    rent_text = deed_font_main.render('Rent £' + str(deed_vals[2]), True, (0,0,0)) #Rent on the unimproved property
    f_width, f_height = deed_font_main.size('Rent £' + str(deed_vals[2]))
    deed_screen.blit(rent_text, [(225-f_width)/2, 123])

    ch_text1 = deed_font_main.render('With 1 Council House', True, (0,0,0)) #Basic text providing a textual explanation for the 4 rent values with Council Houses
    deed_screen.blit(ch_text1, [15, 153])
    ch_text2 = deed_font_main.render('With 2 Council Houses', True, (0,0,0))
    deed_screen.blit(ch_text2, [15, 173])
    ch_text3 = deed_font_main.render('With 3 Council Houses', True, (0,0,0))
    deed_screen.blit(ch_text3, [15, 193])
    ch_text4 = deed_font_main.render('With 4 Council Houses', True, (0,0,0))
    deed_screen.blit(ch_text4, [15, 213])

    ch_rent1 = deed_font_main.render('£' + str(deed_vals[3]), True, (0,0,0)) #Rent values for 1, 2, 3 and 4 council houses
    f_width, f_height = deed_font_main.size('£' + str(deed_vals[3]))
    deed_screen.blit(ch_rent1, [210-f_width, 153])
    ch_rent2 = deed_font_main.render('£' + str(deed_vals[4]), True, (0,0,0))
    f_width, f_height = deed_font_main.size('£' + str(deed_vals[4]))
    deed_screen.blit(ch_rent2, [210-f_width, 173])
    ch_rent3 = deed_font_main.render('£' + str(deed_vals[5]), True, (0,0,0))
    f_width, f_height = deed_font_main.size('£' + str(deed_vals[5]))
    deed_screen.blit(ch_rent3, [210-f_width, 193])
    ch_rent4 = deed_font_main.render('£' + str(deed_vals[6]), True, (0,0,0))
    f_width, f_height = deed_font_main.size('£' + str(deed_vals[6]))
    deed_screen.blit(ch_rent4, [210-f_width, 213])

    tb_rent = deed_font_main.render('With Tower Block £' + str(deed_vals[7]), True, (0,0,0)) #Rent with a tower block on the property
    f_width, f_height = deed_font_main.size('With Tower Block £' + str(deed_vals[7]))
    deed_screen.blit(tb_rent, [(225-f_width)/2, 233])

    mortgage_val = deed_font_main.render('Mortgage Value £' + str(deed_vals[10]), True, (0,0,0)) #Mortgage value on property
    f_width, f_height = deed_font_main.size('Mortgage Value £' + str(deed_vals[10]))
    deed_screen.blit(mortgage_val, [(225-f_width)/2, 260])

    ch_cost = deed_font_main.render('Council Houses cost £' + str(deed_vals[8]) + ' each', True, (0,0,0)) #Cost of a council house for this property
    f_width, f_height = deed_font_main.size('Council Houses cost £' + str(deed_vals[8]) + ' each')
    deed_screen.blit(ch_cost, [(225-f_width)/2, 280])

    tb_cost = deed_font_main.render('Tower Block costs £' + str(deed_vals[9]) + ',', True, (0,0,0)) #Cost of a tower block for this property
    f_width, f_height = deed_font_main.size('Tower Block costs £' + str(deed_vals[9]) + ',')
    deed_screen.blit(tb_cost, [(225-f_width)/2, 300])
    tb_info = deed_font_main.render('plus 4 Council Houses', True, (0,0,0))
    f_width, f_height = deed_font_main.size('plus 4 Council Houses')
    deed_screen.blit(tb_info, [(225-f_width)/2, 318])

    bottom_note1 = deed_font_bottom.render('If a player owns all properties in this', True, (0,0,0)) #Note at bottom of the title deed about rent doubling 
    f_width, f_height = deed_font_bottom.size('If a player owns all properties in this') #if all properties in a group are owned and unimproved
    deed_screen.blit(bottom_note1, [(225-f_width)/2, 350])
    bottom_note2 = deed_font_bottom.render('group, rent is doubled on properties with', True, (0,0,0))
    f_width, f_height = deed_font_bottom.size('group, rent is doubled on properties with')
    deed_screen.blit(bottom_note2, [(225-f_width)/2, 364])
    bottom_note3 = deed_font_bottom.render('no Council Houses or Tower Blocks', True, (0,0,0))
    f_width, f_height = deed_font_bottom.size('no Council Houses or Tower Blocks')
    deed_screen.blit(bottom_note3, [(225-f_width)/2, 378])

    return deed_screen
