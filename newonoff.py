import pygame
from pygame.locals import *
import ctypes
import os

from cls import Button

# Player chooses whether a new game will be online or played over a network
def NewOnOff(clock): 
    pygame.init()

    #Set width and height of the pygame screen
    height = 250
    width = 768

    font_48 = pygame.font.SysFont('Arial', 48)
    font_60 = pygame.font.SysFont('Arial', 60)

    buts = [Button((width-400)/3, 120, 200, 80, "Offline", font_48),
            Button(200+2*(width-400)/3, 120, 200, 80, "Networked", font_48)]

    mode_buts = [Button((width-400)/3, 120, 200, 80, "Host", font_48, visible=False),
                Button(200+2*(width-400)/3, 120, 200, 80, "Connect", font_48, visible=False)]
    title_text = font_60.render("Choose your Game Mode:", True, (255,255,255))
    t_width, t_height = font_60.size("Choose your Game Mode:")
    pc_img = pygame.transform.smoothscale(pygame.image.load("img/PC.png"), [height, height])
    
    overlay = pygame.Surface((width,height), pygame.SRCALPHA)
    overlay.fill((0,0,0,196))

    user32 = ctypes.windll.user32
    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % ((screen_w - width)/2,(screen_h - height)/2)

    screen = pygame.display.set_mode([width,height], pygame.NOFRAME)
    screen.fill((0,0,0))

    running = True
    while running:
        for event in pygame.event.get():
            for but in buts:
                but.handle_input_event(event)
            for but in mode_buts:
                but.handle_input_event(event)
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: #If escape key is pressed
                    running = False #Game exists completely
                    pygame.quit() 
              
        screen.fill((0,0,0))
        screen.blit(pc_img, [0,0])
        screen.blit(overlay, (0,0))
        screen.blit(title_text, [(width-t_width)/2, 30])

        #Display the buttons
        for but in buts:
            but.render(screen)
        for but in mode_buts:
            but.render(screen)
        
        if buts[0].clicked():
            running = False
            gotoScreen = 0
        elif buts[1].clicked():
            gotoScreen = 5
            mode_buts[0].showBut()
            mode_buts[1].showBut()
            buts[0].hideBut()
            buts[1].hideBut()
        
        if mode_buts[0].clicked():
            running = False
            mode = "Host"
        elif mode_buts[1].clicked():
            running = False
            mode = "Connect"

        clock.tick(10)
        pygame.display.flip() #Update display
    return gotoScreen, mode #0 = Offline, 5 = Networked online