import pygame

class Button:
    def __init__(self, x, y, w, h, cap, font, but_col = (100, 100, 100), txt_col = (0,0,0)):
        self.but_x = x
        self.but_y = y
        self.but_w = w
        self.but_h = h
        self.but_caption = cap
        self.but_font = font
        self.but_col = but_col
        self.txt_col = txt_col
        
        self.but_rect = Pygame.Rect(x, y, w, h)

        f_width, f_height = font.size(self.but_caption)
        self.txt_x = (self.but_w - f_width)/2 + self.but_x
        self.txt_y = (self.but_h - f_height)/2 + self.but_y

        self.cap_text = font.render(self.but_caption, True, self.txt_col)

    def render(self, screen):
        pygame.draw.rect(screen, self.but_col, self.but_rect)

        screen.blit(self.cap_text, [self.txt_x, self.txt_y]) #Displays the text in the centre of the button

    def clicked(self, mouse_pos):
        if self.but_rect.collidepoint(mouse_pos):
            return True
        else:
            return False

    def updateCap(self, new_cap):
        self.but_caption = new_cap

        f_width, f_height = font.size(self.but_caption)
        self.txt_x = (self.but_w - f_width)/2 + self.but_x
        self.txt_y = (self.but_h - f_height)/2 + self.but_y

        self.cap_text = font.render(self.but_caption, True, self.txt_col)