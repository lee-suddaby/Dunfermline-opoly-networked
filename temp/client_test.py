import Pyro4
import socket

lobby = Pyro4.Proxy("PYRONAME:dfo.lobby")
print(lobby.connect(socket.gethostbyname(socket.gethostname()), socket.gethostname()))
print(lobby.connect("192.168.1.75", "Lee"))
print(lobby.getLobby())