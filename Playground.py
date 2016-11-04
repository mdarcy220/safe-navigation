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
        self.map_modifiers = [None]
        self.init_map_modifiers()
        self.LoadMap(self.MapName)


    def init_map_modifiers(self):
        self.map_modifiers.append(self.Map1);
        self.map_modifiers.append(self.Map2);
        self.map_modifiers.append(self.Map3);
        self.map_modifiers.append(self.Map4);
        self.map_modifiers.append(self.Map5);
        self.map_modifiers.append(None); 
        self.map_modifiers.append(self.Map7);
        self.map_modifiers.append(self.Map8);
        self.map_modifiers.append(self.Map9);
        self.map_modifiers.append(self.Map10);


    def LoadMap(self, Mapname):
        image                   = PG.image.load(self.MapName)
        self.Playground         = image
        if (self.cmdargs):
            self.apply_map_modifier_by_number(image, self.cmdargs.map_modifier_num)
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
                    
        

    def apply_map_modifier_by_number(self, image, modifier_num):

        if (len(self.map_modifiers) <= modifier_num):
            return
        map_modifier = self.map_modifiers[modifier_num]
        if map_modifier is None:
            return

        map_modifier(image)

    def make_randompath_dynamic_obstacle(self,
                                        x_low=1,
                                        x_high=None,
                                        y_low=1,
                                        y_high=None,
                                        radius_low=5,
                                        radius_high=40,
                                        shape=1,
                                        speed_low=1.0,
                                        speed_high=9.0,
                                        num_path_points=15,
                                        path_x_low=1,
                                        path_x_high=None,
                                        path_y_low=1,
                                        path_y_high=None):
        x_high = self.width if x_high is None else x_high
        y_high = self.width if y_high is None else y_high
        path_x_high = self.width if path_x_high is None else path_x_high
        path_y_high = self.width if path_y_high is None else path_y_high
 
        dynobs = DynamicObs()
        x_coord = int(np.random.uniform(low=x_low, high=x_high))
        y_coord = int(np.random.uniform(low=y_low, high=y_high))
        dynobs.coordinate = (x_coord, y_coord)
        dynobs.origin = dynobs.coordinate
        
        dynobs.movement_mode = 3
        dynobs.radius = int(np.random.uniform(radius_low, radius_high))
        dynobs.shape = shape
        dynobs.speed = np.random.uniform(low=speed_low, high=speed_high)
        for j in range(1, num_path_points):
            x_coord = int(np.random.uniform(path_x_low, path_x_high))
            y_coord = int(np.random.uniform(path_y_low, path_y_high))
            dynobs.path_list.append(np.array([x_coord, y_coord]))
        return dynobs


    def Map1(self, image):

        for i in range(1, 20):
            dynobs = self.make_randompath_dynamic_obstacle(radius_low=10, radius_high=35, speed_high=7.0)
            self.dynamic_obstacles.append(dynobs)
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


    def Map4(self, image):

        for i in range(1, 20):
            dynobs = self.make_randompath_dynamic_obstacle()
            self.dynamic_obstacles.append(dynobs)
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


    def Map5(self, image):

        for i in range(1, 20):
            dynobs = self.make_randompath_dynamic_obstacle(radius_low=10, radius_high=25)
            self.dynamic_obstacles.append(dynobs)
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


    def Map9(self, image):
        for i in range(1, 20):
            dynobs = self.make_randompath_dynamic_obstacle()
            self.dynamic_obstacles.append(dynobs)

    # Swarm of obstacles
    def Map10(self, image): 
        for i in range(1, 120):
            dynobs = self.make_randompath_dynamic_obstacle(radius_low=10, radius_high=15, speed_high=11.0)
            self.dynamic_obstacles.append(dynobs)


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
