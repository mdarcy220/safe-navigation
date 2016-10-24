import numpy  as np
import pygame as PG
import math
from Radar import  Radar_Object
import Distributions
import Vector
import matplotlib.pyplot as plt
import time

class Robot_Object(object):
    def __init__(self, screen,  Target_Object, StartLocation, speed = 3, cmdargs=None, issafe = False):
        self.cmdargs            = cmdargs
        self.location           = StartLocation
        self.TargetObj          = Target_Object
        self.speed              = speed
        self.radar              = Radar_Object(screen)
        self.PathList           = []
        self.PDF                = Distributions.Distributions()
        self.IAmSafe            = issafe
        # Function that selects an angle based on a distribution
        self.pdf_angle_selector = self.center_of_gravity_pdfselector
        # Function that combines pdfs
        self.combine_pdfs       = np.minimum

        # Memory of visited points
        self.visited_points     = []
        # Stores the memory and movement vectors (for drawing in debug mode)
        self.last_mbv           = [0,0]
        self.last_mmv           = [0,0]

        # Number of times NextStep was called
        self.stepNum            = 0

        # Used to allow real-time plotting
        if (not (self.cmdargs is None)) and (cmdargs.show_real_time_plot):
            plt.ion()
            plt.show()


    def SetSpeed(self, speed):
        self.speed = speed


    def Gaussian_noise(self, pdf):
        noise_pdf = np.random.normal(0, 0.02, pdf.size) + pdf
        return noise_pdf


    def NextStep(self, grid_data):
        if (self.distanceToTarget() < 20):
            return True
        self.stepNum += 1

        targetpoint_pdf = self.PDF.Radar_GaussianDistribution(self.angleToTarget())
        if (not (self.cmdargs is None)) and (self.cmdargs.target_distribution_type == 'rectangular'):
            targetpoint_pdf = self.PDF.Radar_RectangularDistribution(self.angleToTarget())
        elif (not (self.cmdargs is None)) and (self.cmdargs.target_distribution_type == 'dotproduct'):
            targetpoint_ang = self.angleToTarget()
            targetpoint_pdf = np.array([(self.speed*(np.cos(np.abs(targetpoint_ang - ang) * np.pi/180)+1)/2) for ang in np.arange(0, 360, self.PDF.DegreeResolution)], dtype='float64')
            targetpoint_pdf = (targetpoint_pdf/np.amax(targetpoint_pdf)) * 0.8 + 0.2

        self.combined_pdf = targetpoint_pdf
        RadarData = self.Gaussian_noise(self.radar.ScanRadar(self.location, grid_data))
        self.combined_pdf = self.combine_pdfs(self.combined_pdf, RadarData)

        if (not (self.cmdargs is None)) and (self.cmdargs.enable_memory):
            # Get memory effect vector
            mem_bias_vec = self.calc_memory_bias_vector()
            self.last_mbv = mem_bias_vec

            mem_bias_ang = Vector.getAngleBetweenPoints((0,0), mem_bias_vec)
            mem_bias_mag = Vector.getDistanceBetweenPoints((0,0), mem_bias_vec)
            
            mem_bias_pdf = np.array([(np.cos(np.abs(mem_bias_ang-ang) * np.pi/180)) for ang in np.arange(0, 360, self.PDF.DegreeResolution)])
            if np.amax(mem_bias_pdf) > 0:
                mem_bias_pdf = mem_bias_pdf / np.amax(mem_bias_pdf) * 0.75
            mem_bias_pdf = mem_bias_pdf + 0.25
            self.combined_pdf = self.combine_pdfs(self.combined_pdf, mem_bias_pdf)

            if (self.stepNum % 1) == 0:
                self.visited_points.append(self.location)

        movement_ang = self.pdf_angle_selector(self.combined_pdf) * self.PDF.DegreeResolution

        if (not (self.cmdargs is None)) and (self.cmdargs.show_real_time_plot):
            plt.cla()
            plt.plot(self.combined_pdf)
            plt.plot(targetpoint_pdf)
            plt.plot(mem_bias_pdf)
            plt.plot(RadarData)
            plt.axis([0,360,0,1.1])
            plt.pause(0.00001)

        movement_vec = np.array([np.cos(movement_ang * np.pi / 180), np.sin(movement_ang * np.pi / 180)], dtype='float64') * self.speed
        self.last_mmv = movement_vec
        movement_vec = np.array(movement_vec, dtype=int)
        new_location = np.add(self.location, movement_vec)

        if not (grid_data[int(new_location[0]), int(new_location[1])] == 1):
            self.location = new_location
        else:
            print('Robot glitched into obstacle!')
            self.location = np.add(self.location, -movement_vec*1.5)

        self.PathList.append(np.array(self.location, dtype=int))

        return False


    def center_of_gravity_pdfselector(self, pdf):
        width = 60
        maxval_ind = np.argmax(pdf)
        sum_num = 0
        sum_den = 0
        minrange = int(maxval_ind - width / 2)
        maxrange = int(maxval_ind + width/2)
        for n in np.arange(minrange, maxrange , 1 ):
            ind = n
            if n < 0: 
                ind = n + 360
            if n > 359:
                ind = n - 360
            sum_num += pdf[ind]*n
            sum_den += pdf[ind]
        center_of_mass = int(sum_num / (sum_den + 0.00001)) # Add a small number (0.0001) in case sum_den is 0          
        if center_of_mass < 0: 
            center_of_mass += 360
        if center_of_mass > 359:
            center_of_mass -= 360
        return center_of_mass


    def threshold_midpoint_pdfselector(self, pdf):
        maxval_ind = np.argmax(pdf)
        maxval = pdf[maxval_ind]
        threshold = 0.8 * maxval
        runStart = 0
        runLen = 0
        runPos = 0
        bestLen = 0
        bestStart = maxval_ind
        while runPos < len(pdf):
            if threshold <= pdf[runPos]:
                runLen += 1
            else:
                if bestLen < runLen:
                    bestStart = runStart
                    bestLen = runLen
                runStart = runPos
                runLen = 0
            runPos += 1
        return bestStart+int(bestLen/2)


    def max_value_pdfselector(self, pdf):
        return np.argmax(pdf)


    def calc_memory_bias_vector(self):
        sigmaSquared = 10 ** 2
        gaussian_derivative = lambda x: -0.1*x*(np.exp(-(x*x/(2*sigmaSquared))) / sigmaSquared)
        vec = np.array([0, 0], dtype='float64')
        for point in self.visited_points:
        #for point in [PG.mouse.get_pos()]:
            effect_magnitude = gaussian_derivative(Vector.getDistanceBetweenPoints(point, self.location))
            effect_vector = effect_magnitude * np.subtract(point, self.location)
            vec += effect_vector
        return vec


    def draw(self, screen):
        # Be careful when uncommenting things in this function.
        # Each line drawn makes it more likely that the robot goes through obstacles
        #PG.draw.circle(screen, (0, 0, 255), np.array(self.location, dtype=int), 4, 0)
        BlueColor  = (0,0,255)
        GreenColor = (10, 100,10)
        if (self.IAmSafe):
            PathColor = GreenColor
        else:
            PathColor = BlueColor
        for ind, o in enumerate(self.PathList):
            if ind == len(self.PathList) - 1:
                continue

            PG.draw.line(screen,PathColor,self.PathList[ind], self.PathList[ind +1], 3)
        if (not (self.cmdargs is None)) and (0 < self.cmdargs.debug_level):
            # Draw line representing memory effect
            #PG.draw.line(screen, (0,255,0), np.array(self.location, dtype=int), np.array(self.location+self.last_mbv*100, dtype=int), 1)

            # Draw line representing movement
            #PG.draw.line(screen, (255,0,0), np.array(self.location, dtype=int), np.array(self.location+self.last_mmv*100, dtype=int), 1)

            # Draw circle representing radar range
            PG.draw.circle(screen, PathColor, np.array(self.location, dtype=int), self.radar.RadarRadius, 2)

            # Draw distribution values around robot
            #self.draw_pdf(screen, self.combined_pdf)


    def draw_pdf(self, screen, pdf):
        scale = self.radar.RadarRadius
        last_point = [self.location[0]+pdf[0]*scale, self.location[1]]
        for index in np.arange(0, len(pdf), 1):
            ang = index*self.PDF.DegreeResolution*np.pi/180
            cur_point = self.location + scale*pdf[index]*np.array([np.cos(ang), np.sin(ang)], dtype='float64')
            PG.draw.line(screen, (0,200,200), last_point, cur_point, 1)
            last_point = cur_point


    def distanceToTarget(self):
        return Vector.getDistanceBetweenPoints(self.TargetObj.Coordinate, self.location)

    def angleToTarget(self):
        return Vector.getAngleBetweenPoints(self.location, self.TargetObj.Coordinate)
