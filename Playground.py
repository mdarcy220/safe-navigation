import numpy  as np
import pygame as PG
from  DynamicObstacles import DynamicObs
class Playground_Object(object):

    def __init__(self, Width, Height, MapName, position = (0,0), cmdargs=None):
        self.cmdargs            = cmdargs
        self.width    = Width
        self.height   = Height
        self.GridData           = np.zeros((self.width,self.height ), dtype=int)
        self.MapName            = MapName
        self.Position           = position
        self.dynamic_obstacles   = []
        self.LoadMap(self.MapName)


    def LoadMap(self, Mapname):
        image                   = PG.image.load(self.MapName)
        self.Playground         = image
        if (self.cmdargs):
            self.apply_map_modifier(image, self.cmdargs.map_modifier_num)
        self.SetSpeeds(self.cmdargs.speedmode)

    def SetSpeeds(self, speedmode):
        #1  Obstacles Slower
        #2  Obstalces Faster
        #3  Obstacles same as Robot
        #4  Obstacles 50% faster and 50% slower
        #5  Robot Speed is always fastest
        
        
        if speedmode > 6:
            speedmode = 1    
        for DO in self.dynamic_obstacles:
            if speedmode == 4:
                DO.speed = np.array ([4, 10])[np.random.randint(2)]  #Obstalces will be 4 or 10
            elif speedmode == 3:
                DO.speed = 6  #Obstacles will be equal to Robot
            elif (speedmode == 2 or speedmode ==5):
                DO.speed = 10
            elif speedmode == 1:
                DO.speed = 4         
                    
        

    def apply_map_modifier(self, image, modifier_num):

        if (modifier_num == 1):
            self.Map1(image)
        elif (modifier_num == 2):
            self.Map2(image)
        elif (modifier_num == 3):
            self.Map3(image)
        elif (modifier_num == 4):
            self.Map4(image)
        elif (modifier_num == 5):
            self.Map5(image)
        elif (modifier_num == 6):
            self.Map6(image)
        elif (modifier_num == 7):
            self.Map7(image)
        elif (modifier_num == 8):
            self.Map8(image)
        elif (modifier_num == 9):
            self.Map9(image)
        else:
            return


    def Map9(self, image):
        for i in range(1, 10):
            dynobs = DynamicObs()
            x_coord = int(np.random.uniform(low=1, high=self.width))
            y_coord = int(np.random.uniform(low=1, high=self.height))
            dynobs.coordinate = (x_coord, y_coord)
            dynobs.origin = dynobs.coordinate
            
            dynobs.movement_mode = 3
            dynobs.radius = int(np.random.uniform(5, 40))
            dynobs.shape = 1
            dynobs.speed = np.random.uniform(low=1.0, high=9.0)
            for j in range(1, 10):
                x_coord = int(np.random.uniform(50, self.width))
                y_coord = int(np.random.uniform(50, self.height))
                dynobs.path_list.append(np.array([x_coord, y_coord]))
            self.dynamic_obstacles.append(dynobs)


    def Map7(self, image):
        x = [200, 300, 440, 560]
        y = [50, 200, 350, 500]

        for ind,i in enumerate(y):
            temp = DynamicObs()
            temp.coordinate = (x[0], i)
            temp.origin = (x[0], i)
            temp.movement_mode = 2
            temp.radius = 50
            temp.shape = 1
            self.dynamic_obstacles.append(temp)
        for ind, i in enumerate(y):
            temp = DynamicObs()
            temp.coordinate = (x[2], i)
            temp.origin = (x[2], i)
            temp.movement_mode = 2
            temp.radius = 50
            temp.shape = 1
            self.dynamic_obstacles.append(temp)

        for ind, i in enumerate(y):
            temp = DynamicObs()
            temp.coordinate = (x[1], i)
            temp.origin =  (x[1], i)
            temp.movement_mode = 1
            temp.size = [50,50]
            temp.shape = 2
            self.dynamic_obstacles.append(temp)
        for ind, i in enumerate(y):
            temp = DynamicObs()
            temp.coordinate = (x[3], i)
            temp.origin = (x[3], i)
            temp.movement_mode = 1
            temp.size = [50, 50]
            temp.shape = 2
            self.dynamic_obstacles.append(temp)

    def Map8(self, image):

        x = [100, 400, 600, 100,700,650]
        y = [50, 350, 175, 200, 400,500]
        for ind,i in enumerate (x):
            temp = DynamicObs()
            temp.coordinate = (i, y[ind])
            temp.origin = (i, y[ind])
            temp.movement_mode = 2
            temp.radius = 20
            temp.shape = 1
            self.dynamic_obstacles.append(temp)


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
            temp.movement_mode = 2
            temp.radius = int(np.random.uniform(10, 20))
            temp.shape = 1
            self.dynamic_obstacles.append(temp)
        for j in np.arange(10):
            temp = DynamicObs()
            x = int(np.random.uniform(0, 800))
            y = int(np.random.uniform(0, 600))
            temp.coordinate = (x, y)
            temp.origin = (x, y)
            temp.movement_mode = 1
            temp.size = [int(np.random.uniform(10, 20)), int(np.random.uniform(10, 20))]
            temp.shape = 2
            self.dynamic_obstacles.append(temp)


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
            temp.movement_mode = 2
            temp.radius = int(np.random.uniform(10, 20))
            temp.shape = 1
            self.dynamic_obstacles.append(temp)
        for j in np.arange(10):
            temp = DynamicObs()
            x = int(np.random.uniform(0, 800))
            y = int(np.random.uniform(0, 600))
            temp.coordinate = (x, y)
            temp.origin = (x, y)
            temp.movement_mode = 1
            temp.size = [int(np.random.uniform(10, 20)), int(np.random.uniform(10, 20))]
            temp.shape = 2
            self.dynamic_obstacles.append(temp)



    def Map3(self, image):
        for j in np.arange(8):
            temp = DynamicObs()
            x = int(np.random.uniform(100, 700))
            y = int(np.random.uniform(150, 450))
            temp.coordinate = (x,y)
            temp.origin   = (x,y)
            temp.movement_mode = 2
            temp.radius = int(np.random.uniform(20, 30))
            temp.shape = 1
            self.dynamic_obstacles.append(temp)


    def Map3(self, image):
        for j in np.arange(8):
            temp = DynamicObs()
            x = int(np.random.uniform(100, 700))
            y = int(np.random.uniform(150, 450))
            temp.coordinate = (x,y)
            temp.origin   = (x,y)
            temp.movement_mode = 2
            temp.radius = int(np.random.uniform(20, 30))
            temp.shape = 1
            self.dynamic_obstacles.append(temp)



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
        temp1.movement_mode = 2
        temp1.radius = 50
        temp1.shape = 1


        temp2 = DynamicObs()
        temp2.coordinate = (x2, y2)
        temp2.origin = (x2, y2)
        temp2.movement_mode = 2
        temp2.radius = 50
        temp2.shape = 1


        temp3 = DynamicObs()
        temp3.coordinate = (x3, y3)
        temp3.origin = (x3, y3)
        temp3.movement_mode = 2
        temp3.radius = 50
        temp3.shape = 1

        self.dynamic_obstacles.append(temp1)
        self.dynamic_obstacles.append(temp2)
        self.dynamic_obstacles.append(temp3)


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
            temp.movement_mode = 2
            temp.radius = int(np.random.uniform(20, 30))
            temp.shape = 1
            self.dynamic_obstacles.append(temp)
        for j in np.arange(4):
            temp = DynamicObs()
            x = int(np.random.uniform(100, 700))
            y = int(np.random.uniform(150, 450))
            temp.coordinate = (x, y)
            temp.origin = (x, y)
            temp.movement_mode = 1
            temp.size = [int(np.random.uniform(20, 30)),int(np.random.uniform(20, 30))]
            temp.shape = 2
            self.dynamic_obstacles.append(temp)

    def Nextstep (self, display):
        tempbackground = self.Playground
        display.blit(tempbackground, self.Position)
        for i in self.dynamic_obstacles:
            i.NextStep()
            if (i.shape == 1):
                PG.draw.circle(display, i.fillcolor, np.array(i.coordinate, dtype='int64'), i.radius)
                #PG.draw.circle(display, i.bordercolor, i.coordinate, i.radius, int (i.radius/3))
            if (i.shape == 2):
                PG.draw.rect(display, i.fillcolor, i.coordinate + i.size)
                #PG.draw.rect(display, i.bordercolor, i.coordinate + i .size, int(i.size[0] / 3))

        # Set GridData to 1 where the corresponding pixel is obstacle-colored
        # Note: This approach forces GridData to be at least as large as the pixel array,
        # potentially wasting some memory compared to using a nested for loop. It is
        # written this way intentionally to improve computation time (>1000%)
        pix_arr = PG.surfarray.pixels2d(display)
        # Mask pixel data to account for small errors in color
        # Note: This only works because it has been determined through 
        # experimentation that almost all color errors occur in the last two
        # bits of the value.
        pixel_mask = 0b11111100
        masked_pix_arr = np.bitwise_and(pix_arr, np.array([pixel_mask], dtype='uint8'))

        grid_data_width = max(self.width, masked_pix_arr.shape[0])
        grid_data_height = max(self.height, masked_pix_arr.shape[1] )
        self.GridData = np.zeros((grid_data_width, grid_data_height), dtype=int)

        obstacle_pixel_val = 0x555555 & pixel_mask # (85, 85, 85) represented as integer
        self.GridData[masked_pix_arr == obstacle_pixel_val] = 1

        dynamic_obstacle_pixel_val = 0x227722 & pixel_mask # (34, 119, 34) represented as integer
        self.GridData[masked_pix_arr == dynamic_obstacle_pixel_val] = 3
        
        # Uncomment the following two lines to see the GridData directly
        pix_arr[self.GridData==0] = 0
        pix_arr[self.GridData==3] = 0x115599
        pix_arr[self.GridData==1] = 0xFFFFFF
