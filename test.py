#!/usr/bin/python3

from Polygon import Polygon
import numpy as np
from Human import Human
import Geometry
import math

# test of polygon definition and line detection

polygon_1_list = np.array([[2,10],[12,10],[12,4]])
polygon_2_list = np.array([[2,5],[7,5],[7,4],[9,4],[9,3],[2,3]])
line_1 = np.array([[10,0],[10,10]]) 
line_2 = np.array([[0,0],[250/13,10]]) 

# polygon 1
print("defining polygon with points list:")
for i in range(polygon_1_list.shape[0]):
    print (polygon_1_list[i,:])
print ('\n')
polygon_1 = Polygon(polygon_1_list)
print("polygon's points are:",polygon_1.Points,'\n')
# intersection polygon 1 with line 1 
print("defining line with points:")
print (line_1[0,:])
print (line_1[1,:])
print ("intersection of this line with the above polygon:")
p1_l1 =  polygon_1.line_intersection(line_1)
print (p1_l1)
print("correct intersections are:")
print (np.array([[10,10],[10,5.2]]))
print ('\n')

# intersection polygon 1 with line 1 
print("defining line with points:")
print (line_2[0,:])
print (line_2[1,:])
print ("intersection of this line with the above polygon:")
p1_l2 =  polygon_1.line_intersection(line_2)
print (p1_l2)
print("correct intersections are:")
print (np.array([[12,6.24],[10,5.2]]))
print ('\n')

# polygon 2
print("defining polygon with points list:")
for i in range(polygon_2_list.shape[0]):
    print (polygon_2_list[i,:])
polygon_2 = Polygon(polygon_2_list)

line_3 = np.array([[2,3],[3,5]]) 
line_4 = np.array([[9,3.5],[8.8,4]]) 
line_5 = np.array([[2,3],[2,5]])

# intersection polygon 2 with line 3 
print("defining line with points:")
print (line_3[0,:])
print (line_3[1,:])
print ("intersection of this line with the above polygon:")
p2_l3 =  polygon_2.line_intersection(line_3)
print (p2_l3)
print("correct intersections are:")
print (np.array([[2,3],[3,5]]))
print ('\n')

# intersection polygon 2 with line 4 
print("defining line with points:")
print (line_4[0,:])
print (line_4[1,:])
print ("intersection of this line with the above polygon:")
p2_l4 =  polygon_2.line_intersection(line_4)
print (p2_l4)
print("correct intersections are:")
print (np.array([[9,3.5],[8.8,4]]))
print ('\n')

# intersection polygon 2 with line 5 
print("defining line with points:")
print (line_5[0,:])
print (line_5[1,:])
print ("intersection of this line with the above polygon:")
p2_l5 =  polygon_2.line_intersection(line_5)
print (p2_l5)
print("correct intersections are:")
print (np.array([[2,3],[2,5]]))
print ('\n')


# test of Human definition and line detection

line_1 = np.array([[0,0],[1,1]]) 
line_2 = np.array([[0,1],[1,4]]) 
line_3 = np.array([[0,6],[2,6]]) 
line_4 = np.array([[0,0],[2,0]]) 
line_5 = np.array([[0,0],[0,3]]) 
line_6 = np.array([[4,0],[4,3]]) 

# human 1
print("defining Human:")
human_1 = Human([2,3],4,6,1,0)
# intersection human 1 with line 1 
print("defining line with points:")
print (line_1[0,:])
print (line_1[1,:])
print ("intersection of this line with the above Human:")
h1_l1 =  human_1.line_intersection(line_1)
print (h1_l1)
print("correct intersections are:")
print (np.array([[3.91,3.91],[0.71,0.71]]))
print ('\n')

# intersection human 1 with line 2 
print("defining line with points:")
print (line_2[0,:])
print (line_2[1,:])
print ("intersection of this line with the above Human:")
h1_l2 =  human_1.line_intersection(line_2)
print (h1_l2)
print("correct intersections are:")
print (np.array([[1.65,5.95],[0.22,1.65]]))
print ('\n')

# intersection human 1 with line 3 
print("defining line with points:")
print (line_3[0,:])
print (line_3[1,:])
print ("intersection of this line with the above Human:")
h1_l3 =  human_1.line_intersection(line_3)
print (h1_l3)
print("correct intersections are:")
print (np.array([[2,6]]))
print ('\n')

# intersection human 1 with line 4 
print("defining line with points:")
print (line_4[0,:])
print (line_4[1,:])
print ("intersection of this line with the above Human:")
h1_l4 =  human_1.line_intersection(line_4)
print (h1_l4)
print("correct intersections are:")
print (np.array([[2,0]]))
print ('\n')

# intersection human 1 with line 5 
print("defining line with points:")
print (line_5[0,:])
print (line_5[1,:])
print ("intersection of this line with the above Human:")
h1_l5 =  human_1.line_intersection(line_5)
print (h1_l5)
print("correct intersections are:")
print (np.array([[0,3]]))
print ('\n')

# intersection human 1 with line 6 
print("defining line with points:")
print (line_6[0,:])
print (line_6[1,:])
print ("intersection of this line with the above Human:")
h1_l6 =  human_1.line_intersection(line_6)
print (h1_l6)
print("correct intersections are:")
print (np.array([[4,3]]))
print ('\n')


# test of Human definition and line detection

line_1 = np.array([[0,0],[5+1.5*math.sqrt(2),5-1.5*math.sqrt(2)]]) 
line_2 = np.array([[0,5],[5,5]]) 

# human 2
print("defining Human:")
human_2 = Human([5,5],6,2,1,1)
# intersection human 2 with line 1 
print("defining line with points:")
print (line_1[0,:])
print (line_1[1,:])
print ("intersection of this line with the above Human:")
h2_l1 =  human_2.line_intersection(line_1)
print (h2_l1)
print("correct intersections are:")
print (np.array([[7.12,2.8787]]))
print ('\n')

# intersection human 2 with line 2 
print("defining line with points:")
print (line_2[0,:])
print (line_2[1,:])
print ("intersection of this line with the above Human:")
h2_l2 =  human_2.line_intersection(line_2)
print (h2_l2)
print("correct intersections are(roughly):")
print (np.array([[6.41,5],[3.586,5]]))
print ('\n')

