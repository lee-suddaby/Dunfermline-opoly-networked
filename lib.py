#Functions used in multiple screens, stored here to prevent duplication of code
from cls import *

#Determine how many lines are in a text file
#Used when loading the tips file so the number of tips need not be counted
def getFileLines(filePath):
    with open(filePath) as fh:
        #enumerate is a python-specific function used to loop through all lines in the file and keep an incremental counter automatically, similar to a count occurrences algorithm, except here there is no condition to the counting
        #Slightly simply than manually incrementing a separate counter variable and keeping doing so until the end of the file is reached
        for i, l in enumerate(fh,1):
            pass
    return i

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
def displayButtonRect(screen, rect, but_col, font, caption, txt_col):
    pygame.draw.rect(screen, but_col, rect)

    f_width, f_height = font.size(caption)
    cap_text = font.render(caption, True, txt_col)
    screen.blit(cap_text, [(rect.width-f_width)/2 + rect.left,(rect.height-f_height)/2 + rect.top]) #Displays the text in the centre of the button - (button_width - text_width)/2
