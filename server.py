import Pyro4
from cls_net import Game

#------------------------------Main Server Setup------------------------------ 
def main():
    game = Game()
    Pyro4.Daemon.serveSimple(
        {
            game: "dfo.game"
        },
        ns=True)


if __name__ == "__main__": #This is designed to be run on the console and separately to the DFO game.
    main()