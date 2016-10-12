import numpy as np

class Static_Obstacle(object):
    def __init__(self):
        self.radius     =  0
        self.coordinate = (0,0)
        self.fillcolor  = (0,0,0)

    def SetRadius_randomly(self, min, max):
        self.radius=np.random.uniform(min, max,1)

    def SetCoodinate_randomly(self, leftmargin, rightmargin, topmargin, downmargin, displayheight, displaywidth):
        x = displaywidth  - leftmargin - rightmargin
        y = displayheight - topmargin  - downmargin
        self.coordinate = (np.random.uniform(leftmargin, x, 1), np.random.uniform(topmargin, y, 1))


    def SetCoordinates_Manually(self, Coordinate ):
        self.coordinate = Coordinate

    def SetSizeManually(self, Radius ):
        self.radius = Radius