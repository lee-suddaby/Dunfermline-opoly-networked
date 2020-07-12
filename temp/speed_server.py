import Pyro4
import pygame
pygame.init()

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Speed():
    def __init__(self):
        self.init_ticks = pygame.time.get_ticks()

    def getTime(self):
        return pygame.time.get_ticks() - self.init_ticks


def main():
    speed = Speed()
    Pyro4.Daemon.serveSimple(
        {
            speed: "speed.test"
        },
        ns=True)


if __name__ == "__main__":
    main()