import Pyro4
from cls_net import Game

#------------------------------Main Server Setup------------------------------ 
def main():
    # Read in host (server) IP and port from file.
    # This ensures that (at least on this machine), the client and server will be able to find each other.
    f = open("data/Host_Data.txt", "r")
    host_dat = f.readline().split(",")

    game = Game()
    Pyro4.Daemon.serveSimple(
        {
            game: "dfo.game"
        },
        host=host_dat[0], port=int(host_dat[1]), ns=False, verbose=True)


if __name__ == "__main__": #This is designed to be run on the console and separately to the DFO game.
    main()