import pygame

class Button:
    def __init__(self, x, y, w, h, cap, font, but_col = (100, 100, 100), txt_col = (0,0,0), visible = True, enabled = True):
        self.but_x = x
        self.but_y = y
        self.but_w = w
        self.but_h = h
        self.but_caption = cap
        self.but_font = font
        self.but_col = but_col
        self.txt_col = txt_col
        self.visible = visible
        self.enabled = enabled
        self.MOUSEPRESSED = False
        
        self.but_rect = pygame.Rect(x, y, w, h)

        f_width, f_height = self.but_font.size(self.but_caption)
        self.txt_x = (self.but_w - f_width)/2 + self.but_x
        self.txt_y = (self.but_h - f_height)/2 + self.but_y

        self.cap_text = self.but_font.render(self.but_caption, True, self.txt_col)

        self.overlay = pygame.Surface((self.but_w, self.but_h), pygame.SRCALPHA)
        self.overlay.fill((but_col[0], but_col[1], but_col[2], 196))

    def render(self, screen):
        if self.visible:
            pygame.draw.rect(screen, self.but_col, self.but_rect)
            screen.blit(self.cap_text, [self.txt_x, self.txt_y]) #Displays the text in the centre of the button
            if not self.enabled:
                screen.blit(self.overlay, [self.but_x, self.but_y])

    def handle_input_event(self, event):
        if self.visible and self.enabled:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.MOUSEPRESSED = True
            else:
                self.MOUSEPRESSED = False
        else:
            self.MOUSEPRESSED = False

    def clicked(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.but_rect.collidepoint(mouse_pos) and self.MOUSEPRESSED and self.visible and self.enabled:
            return True
        return False

    def updateCap(self, new_cap):
        self.but_caption = new_cap

        f_width, f_height = self.but_font.size(self.but_caption)
        self.txt_x = (self.but_w - f_width)/2 + self.but_x
        self.txt_y = (self.but_h - f_height)/2 + self.but_y

        self.cap_text = self.but_font.render(self.but_caption, True, self.txt_col)
    
    def hideBut(self):
        self.visible = False

    def showBut(self):
        self.visible = True

    def enableBut(self):
        self.enabled = True
    
    def disableBut(self):
        self.enabled = False
