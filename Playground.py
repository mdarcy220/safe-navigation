import numpy  as np
import pygame as PG
from  DynamicObstacles import DynamicObs
class Playground_Object(object):

    def __init__(self, Width, Height, MapName, position = (0,0)):
        self.PlayGroundWidth    = Width
        self.PlayGroundHeight   = Height
        self.GridData           = np.zeros((self.PlayGroundWidth,self.PlayGroundHeight ), dtype=int)
        self.MapName            = MapName
        self.Position           = position
        self.DynamicObstacles   = []
        self.LoadMap(self.MapName)


    def LoadMap(self, Mapname):
        image                   = PG.image.load(self.MapName)
        self.Playground         = image
        self.Map4(image)


    def Map7(self, image):
        x = [200, 300, 440, 560]
        y = [50, 200, 350, 500]

        for ind,i in enumerate(y):
            temp = DynamicObs()
            temp.coordinate = (x[0], i)
            temp.origin = (x[0], i)
            temp.MovementMode = 2
            temp.radius = 50
            temp.shape = 1
            self.DynamicObstacles.append(temp)
        for ind, i in enumerate(y):
            temp = DynamicObs()
            temp.coordinate = (x[2], i)
            temp.origin = (x[2], i)
            temp.MovementMode = 2
            temp.radius = 50
            temp.shape = 1
            self.DynamicObstacles.append(temp)

        for ind, i in enumerate(y):
            temp = DynamicObs()
            temp.coordinate = (x[1], i)
            temp.origin =  (x[1], i)
            temp.MovementMode = 1
            temp.size = [50,50]
            temp.shape = 2
            self.DynamicObstacles.append(temp)
        for ind, i in enumerate(y):
            temp = DynamicObs()
            temp.coordinate = (x[3], i)
            temp.origin = (x[3], i)
            temp.MovementMode = 1
            temp.size = [50, 50]
            temp.shape = 2
            self.DynamicObstacles.append(temp)

    def Map8(self, image):

        x = [100, 400, 600, 100,700,650]
        y = [50, 350, 175, 200, 400,500]
        for ind,i in enumerate (x):
            temp = DynamicObs()
            temp.coordinate = (i, y[ind])
            temp.origin = (i, y[ind])
            temp.MovementMode = 2
            temp.radius = 20
            temp.shape = 1
            self.DynamicObstacles.append(temp)


    def Map5(self, image):

        for i in np.arange(0, 100, 1):
            x = int(np.random.uniform(100, 700))
            y = int(np.random.uniform(100, 500))
            radius = int(np.random.uniform(5, 30))
            PG.draw.rect(image, (85, 85, 85), (x, y, 20,20))
        for j in np.arange(10):
            temp = DynamicObs()
            x = int(np.random.uniform(0, 800))
            y = int(np.random.uniform(0, 600))
            temp.coordinate = (x, y)
            temp.origin = (x, y)
            temp.MovementMode = 2
            temp.radius = int(np.random.uniform(10, 20))
            temp.shape = 1
            self.DynamicObstacles.append(temp)
        for j in np.arange(10):
            temp = DynamicObs()
            x = int(np.random.uniform(0, 800))
            y = int(np.random.uniform(0, 600))
            temp.coordinate = (x, y)
            temp.origin = (x, y)
            temp.MovementMode = 1
            temp.size = [int(np.random.uniform(10, 20)), int(np.random.uniform(10, 20))]
            temp.shape = 2
            self.DynamicObstacles.append(temp)


    def Map4(self, image):

        for i in np.arange(0, 100, 1):
            x = int(np.random.uniform(0, 800))
            y = int(np.random.uniform(0, 600))
            radius = int(np.random.uniform(5, 30))
            PG.draw.circle(image, (85, 85, 85), (x, y), radius)
        for j in np.arange(10):
            temp = DynamicObs()
            x = int(np.random.uniform(0, 800))
            y = int(np.random.uniform(0, 600))
            temp.coordinate = (x, y)
            temp.origin = (x, y)
            temp.MovementMode = 2
            temp.radius = int(np.random.uniform(10, 20))
            temp.shape = 1
            self.DynamicObstacles.append(temp)
        for j in np.arange(10):
            temp = DynamicObs()
            x = int(np.random.uniform(0, 800))
            y = int(np.random.uniform(0, 600))
            temp.coordinate = (x, y)
            temp.origin = (x, y)
            temp.MovementMode = 1
            temp.size = [int(np.random.uniform(10, 20)), int(np.random.uniform(10, 20))]
            temp.shape = 2
            self.DynamicObstacles.append(temp)



    def Map3(self, image):
        for j in np.arange(8):
            temp = DynamicObs()
            x = int(np.random.uniform(100, 700))
            y = int(np.random.uniform(150, 450))
            temp.coordinate = (x,y)
            temp.origin   = (x,y)
            temp.MovementMode = 2
            temp.radius = int(np.random.uniform(20, 30))
            temp.shape = 1
            self.DynamicObstacles.append(temp)


    def Map3(self, image):
        for j in np.arange(8):
            temp = DynamicObs()
            x = int(np.random.uniform(100, 700))
            y = int(np.random.uniform(150, 450))
            temp.coordinate = (x,y)
            temp.origin   = (x,y)
            temp.MovementMode = 2
            temp.radius = int(np.random.uniform(20, 30))
            temp.shape = 1
            self.DynamicObstacles.append(temp)



    def Map2(self,image):

        x1 = 100
        x2 = 400
        x3 = 600

        y1 = 50
        y2 = 350
        y3 = 175

        temp1 = DynamicObs()
        temp1.coordinate = (x1, y1)
        temp1.origin = (x1, y1)
        temp1.MovementMode = 2
        temp1.radius = 50
        temp1.shape = 1


        temp2 = DynamicObs()
        temp2.coordinate = (x2, y2)
        temp2.origin = (x2, y2)
        temp2.MovementMode = 2
        temp2.radius = 50
        temp2.shape = 1


        temp3 = DynamicObs()
        temp3.coordinate = (x3, y3)
        temp3.origin = (x3, y3)
        temp3.MovementMode = 2
        temp3.radius = 50
        temp3.shape = 1

        self.DynamicObstacles.append(temp1)
        self.DynamicObstacles.append(temp2)
        self.DynamicObstacles.append(temp3)


    def Map1(self, image):

        for i in np.arange(0, 50, 1):
            x = int(np.random.uniform(100, 700))
            y = int(np.random.uniform(150, 450))
            radius = int(np.random.uniform(10, 30))
            PG.draw.circle(image, (85, 85, 85), (x, y), radius)
        for j in np.arange(4):
            temp = DynamicObs()
            x = int(np.random.uniform(100, 700))
            y = int(np.random.uniform(150, 450))
            temp.coordinate = (x,y)
            temp.origin   = (x,y)
            temp.MovementMode = 2
            temp.radius = int(np.random.uniform(20, 30))
            temp.shape = 1
            self.DynamicObstacles.append(temp)
        for j in np.arange(4):
            temp = DynamicObs()
            x = int(np.random.uniform(100, 700))
            y = int(np.random.uniform(150, 450))
            temp.coordinate = (x, y)
            temp.origin = (x, y)
            temp.MovementMode = 1
            temp.size = [int(np.random.uniform(20, 30)),int(np.random.uniform(20, 30))]
            temp.shape = 2
            self.DynamicObstacles.append(temp)

    def Nextstep (self, display):
        tempbackground = self.Playground
        display.blit(tempbackground, self.Position)
        for i in self.DynamicObstacles:
            i.NextStep()
            if (i.shape == 1):
                PG.draw.circle(display, i.fillcolor, i.coordinate, i.radius)
                PG.draw.circle(display, i.bordercolor, i.coordinate, i.radius, int (i.radius/3))
            if (i.shape == 2):
                PG.draw.rect(display, i.fillcolor, i.coordinate + i.size)
                PG.draw.rect(display, i.bordercolor, i.coordinate + i .size, int(i.size[0] / 3))
        self.GridData = np.zeros((self.PlayGroundWidth, self.PlayGroundHeight), dtype=int)
        for x in np.arange(1,self.PlayGroundWidth):
            for y in np.arange (1,self.PlayGroundHeight):
                if (display.get_at((x, y)) == (85, 85, 85) ):
                    self.GridData[x,y] = 1
