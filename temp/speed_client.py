import Pyro4
import pygame

def main():
    pygame.init()
    speed = Pyro4.Proxy("PYRONAME:speed.test")
    clock = pygame.time.Clock()
    while True:
        print(speed.getTime())

        clock.tick(10)



if __name__ == "__main__":
    main()