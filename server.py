import numpy as np
import Pyro4

#------------------------------Lobby and Conn Classes------------------------------ 
@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Lobby():
    def __init__(self):
        self.conns = list()
        self.max_conns = 6

    def getLobby(self):
        ret_lobby = [[0 for x in range(3)] for y in range(len(self.conns))]
        for i in range(len(self.conns)):
            ret_lobby[i][0] = self.conns[i].getIP()
            ret_lobby[i][1] = self.conns[i].getName()
            ret_lobby[i][2] = self.conns[i].getPiece()
        return ret_lobby

    def getConns(self):
        return self.conns

    def getUsedPieces(self):
        used = []
        for conn in self.conns:
            used.append(conn.getPiece())
        return used

    def connect(self, c_ip, c_name):
        for conn in self.conns:
            if conn.getIP() == c_ip: #Avoids duplicate connections:
                return "This IP is already connected"
        if len(self.conns) < self.max_conns:
            self.conns.append(Conn(c_ip, c_name))
            return "Successfully connected"
        else:
            return "Maximum number of connections exceeded"
    
    def disconnect(self, c_ip):
        for i in range(len(self.conns)):
            if self.conns[i].getIP() == c_ip:
                self.conns.pop(i)
                return "Successfully disconnected"
        return "IP not found. Was never connected"
    
    def setPiece(self, c_ip, c_piece):
        for conn in self.conns:
            if conn.getIP() == c_ip:
                conn.setPiece(c_piece)
                return
        return "IP not found"
        

class Conn():
    def __init__(self, c_ip, c_name):
        self.conn_ip = c_ip
        self.conn_name = c_name
        self.conn_piece = 0
    
    def getIP(self):
        return self.conn_ip
    
    def getName(self):
        return self.conn_name
    
    def getPiece(self):
        return self.conn_piece
    
    def setPiece(self, piece_num):
        self.conn_piece = piece_num


#------------------------------Main Server Setup------------------------------ 
def main():
    lobby = Lobby()
    Pyro4.Daemon.serveSimple(
        {
            lobby: "dfo.lobby"
        },
        ns=True)


if __name__ == "__main__": #This is designed to be run on the console and separately to the DFO game.
    main()