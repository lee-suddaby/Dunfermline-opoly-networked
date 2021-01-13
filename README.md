# Dunfermline-opoly
It's in the title: Monopoly recreated around the Scottish town of Dunfermline. Originally made for an Advanced Higher Computing Science project.

## Running the Game

Clone/download the repository, which contains all data files and all assets that the game requires. You may find that you need to install missing modules (e.g. Pyro4) via pip.

### Offline

Playing offline is easy - run `main.py` then click the "Offline" button and fill in the necessary names and so on to start.

### Networked

Dunfermline-opoly can also be played over a local network. If you want to play the networked version of this game, first add the IP for the host in ` data/Host_Data.txt` (replace 0.0.0.0). This uses ipv4, and you can find your (local) address using ipconfig in the command line. The second piece of data (currently 9090) represents the connection port and can be left as is.

The host should first run `server.py`. Then each player runs `main.py` on their machine and selects the "Networked" game option.

## Issues
If you find any bugs, or just want to give feedback, feel free to open an issue.
