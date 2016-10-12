import numpy        as np
from Game import Game_Object

if __name__ == '__main__':
    Game = Game_Object()
    if (Game.GameLoop() == 1):
        print ("Error occured ... ")
    else:
        print ("Completed")
