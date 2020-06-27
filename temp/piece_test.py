import Pyro4

lobby = Pyro4.Proxy("PYRONAME:dfo.lobby")

lobby.connect("192.168.1.755", "Test1")
lobby.connect("192.168.1.756", "Test2")
lobby.connect("192.168.1.757", "Test3")
lobby.connect("192.168.1.758", "Test4")
lobby.connect("192.168.1.759", "Test5")

lobby.setPiece("192.168.1.755", 1)
lobby.setPiece("192.168.1.756", 2)
lobby.setPiece("192.168.1.757", 3)