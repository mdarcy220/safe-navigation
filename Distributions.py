import numpy as np


class Distributions(object):

    def __init__ (self):
        self.Radar_RectangleDistribution_width = 40
        
        self.Radar_GaussianDistribution_Amplitude = 1
        self.Radar_GaussianDistribution_Sigma = 110
        
        self.Memory_GaussianDistribution_Sigmax = 1
        self.Memory_GaussianDistribution_Sigmay = 1
        
        self.DegreeResolution = 1 #This means that, the array starts from 1 and increases by DegreeResolution. like 1, 1+ DegreeResolution, 1+ 2*DegreeResolution ... 360

        self.cached_gaussian_distribution = None
        
    def ResetValues (self, 
                     Radar_RectangleDistribution_width    = 40, 
                     Radar_GaussianDistribution_Sigma      = 1 ,
                     Radar_GaussianDistribution_Amplitude = 1,
                     Memory_GaussianDistribution_Sigmax   = 1 , 
                     Memory_GaussianDistribution_Sigmay   = 1 ):
        self.Radar_RectangleDistribution_width = Radar_RectangleDistribution_width
        
        self.Radar_GaussianDistribution_Amplitude = Radar_GaussianDistribution_Amplitude
        self.Radar_GaussianDistribution_Sigma = Radar_GaussianDistribution_Sigma
        
        self.Memory_GaussianDistribution_Sigmax = Memory_GaussianDistribution_Sigmax
        self.Memory_GaussianDistribution_Sigmay = Memory_GaussianDistribution_Sigmay


    def Radar_RectangularDistribution(self, Center):
        width = self.Radar_RectangleDistribution_width;
        arr = np.zeros(360 / self.DegreeResolution)
        Startpoint = Center -  width / 2
        if (Startpoint < 0):
            Startpoint = Startpoint + 360
        for degree in np.arange (Startpoint, Center + width / 2, self.DegreeResolution):
            if (degree > 360):
                degree = degree - 360
            arr[int(degree / self.DegreeResolution)] = 1
            
        return arr


    def Radar_GaussianDistribution (self, Center):
        if self.cached_gaussian_distribution is None:
            self.cached_gaussian_distribution = self.gen_cached_gaussian();


        return np.roll(self.cached_gaussian_distribution, int(np.round(Center)))

    def gen_cached_gaussian(self):
        
        arr = np.zeros(int(360 / self.DegreeResolution))

        for degree in np.arange (-180, 540, self.DegreeResolution):
            gaussianresult = self.Radar_GaussianDistribution_Amplitude * np.exp((-1 * ((degree) ** 2)) / (2 * (self.Radar_GaussianDistribution_Sigma ** 2)))

            if degree < 0:
                degree = degree + 360
            elif degree >= 360:
                degree = degree - 360
            if arr[int(degree /  self.DegreeResolution)] < gaussianresult :
                arr[int(degree /  self.DegreeResolution)] = gaussianresult

        return arr;

    def Memory_GaussianDistribution(self, Center, xboundary, yboundary): #xyboundary should include the x and y of the grid data.
        arr = np.zeros((yboundary, xboundary))
        for x in np.arange (0, xboundary, 1):
            for y in np.arange (0, yboundary, 1):
                gaussianresult = self.Radar_GaussianDistribution_Amplitude * np.exp(-1 * ( ((x - Center[1])**2)/(2 * (self.Memory_GaussianDistribution_Sigmax)**2 ) +     ((y - Center[0])**2)/(2 * (self.Memory_GaussianDistribution_Sigmay)**2 )))
                arr[y,x] = gaussianresult
        return arr
   
   

