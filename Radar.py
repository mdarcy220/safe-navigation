import numpy as np
import sys
from Circle import *
import Vector
import math

class Radar:

	def __init__(self, env, radius = 100, resolution = 4, degree_step = 1):

		self.env         = env
		self.radius	 = radius
		self.resolution  = resolution
		self.set_degree_step(degree_step);
		self.last_angrange = [0, 360]


	def ScanRadar(self, center, grid_data):

		radar_data = np.ones(int(360 / int(self._degree_step)))
		currentStep = 0
		x_upper_bound = min(799, grid_data.shape[0])
		y_upper_bound = min(599, grid_data.shape[1])
		for degree in np.arange(0, 360, self._degree_step):
			ang_in_radians = degree * np.pi / 180
			cos_cached = np.cos(ang_in_radians)
			sin_cached = np.sin(ang_in_radians)
			for i in np.arange(0, self.radius, self.resolution):
				x = int(cos_cached * i + center[0])
				y = int(sin_cached * i + center[1])
				if ((x < 0) or (y < 0) or (x_upper_bound <= x) or (y_upper_bound <= y)):
					radar_data[currentStep] = i / self.radius
					break
				if (grid_data[x,y] & 1):
					radar_data[currentStep] = i / self.radius
					break
			currentStep = currentStep + 1
		return radar_data


	def set_degree_step(self, newDegreeStep):
		self._degree_step = newDegreeStep;
		# Recalculate beams
		self._nPoints = int(360 / int(self._degree_step)); 
		self._beams = np.zeros([self._nPoints, 2]);
		currentStep = 0
		for angle in np.arange(0, 360, self._degree_step):
			ang_in_radians = angle * np.pi / 180
			self._beams[currentStep] = Vector.unitVectorFromAngle(ang_in_radians) * self.radius
			currentStep += 1


	def get_circle_intersect_angle_range(self, scan_center, circle_center, circle_radius):
		points = circle_circle_intersection(scan_center, self.radius, circle_center, circle_radius);
		if points is None or len(points) < 2:
			return None;
		ang1 = Vector.getAngleBetweenPoints(scan_center, points[0]);
		ang2 = Vector.getAngleBetweenPoints(scan_center, points[1]);
		vec1 = points[0] - scan_center;
		vec2 = points[1] - scan_center;
		crossProd = np.cross(vec1, vec2);
		if crossProd < 0:
			return [ang2, ang1];
		elif crossProd > 0:
			return [ang1, ang2];
		else:
			return [0, 360];


	def get_circle_angle_range(self, scan_center, circle_center, circle_radius):
		if Vector.getDistanceBetweenPoints(scan_center, circle_center) < self.radius:
			return self.get_circle_shadow_angle_range(scan_center, circle_center, circle_radius);
		else:
			return self.get_circle_intersect_angle_range(scan_center, circle_center, circle_radius);


	def get_circle_shadow_angle_range(self, scan_center, circle_center, circle_radius):
		base_ang = Vector.getAngleBetweenPoints(scan_center, circle_center);
		dist = Vector.getDistanceBetweenPoints(scan_center, circle_center);
		if dist < circle_radius:
			return [0, 360];
		offset = np.arcsin(circle_radius / float(dist)) * 180.0 / np.pi;
		if np.isnan(offset):
			return [0, 360];
		else:
			return [base_ang - offset, base_ang + offset];


	def line_line_intersection(line1, line2):
		vec_line1 = line1[1] - line1[0];
		vec_line2 = line2[1] - line2[0];
		crossProd = np.cross(vec_line1, vec_line2)

		if crossProd == 0:
			return None;

		t = np.cross(line2[0] - line1[0], vec_line2) / crossProd
		u = np.cross(line2[0] - line1[0], vec_line1) / crossProd

		if 0 <= t and t <= 1 and 0 <= u and u <= 1:
			return line1[0] + (t * vec_line1);
		return None;


	def rectangle_line_intersection(rect, line):
		# Rectangle should be a list of [np.array([x, y]), np.array([width, height])]
		# Line should be [np.array([x1, y1]), np.array([x2, y2])]

		inters = []

		# Make a list of points IN THE ORDER THEY ARE CONNECTED
		rect_points = [rect[0]]
		rect_points.append(rect[0] + np.array([rect[1][0], 0]))
		rect_points.append(rect[0] + rect[1])
		rect_points.append(rect[0] + np.array([0, rect[1][1]]))

		rect_lines = [];
		rect_lines.append(np.array([rect_points[0], rect_points[1]]));
		rect_lines.append(np.array([rect_points[1], rect_points[2]]));
		rect_lines.append(np.array([rect_points[2], rect_points[3]]));
		rect_lines.append(np.array([rect_points[3], rect_points[0]]));

		for rect_line in rect_lines:
			inter = Radar.line_line_intersection(line, rect_line);
			if not (inter is None):
				inters.append(inter);

		return inters;


	def get_rectangle_shadow_angle_range(self, scan_center, rect_pos, rect_dim):
		rect_points = [rect_pos]
		rect_points.append(rect_pos + np.array([rect_dim[0], 0]))
		rect_points.append(rect_pos + rect_dim)
		rect_points.append(rect_pos + np.array([0, rect_dim[1]]))

		first_ang = Vector.getAngleBetweenPoints(scan_center, rect_points[0]);

		angle_range = [first_ang, first_ang];

		for point in rect_points[1:]:
			vec = point - scan_center;
			vec2 = Vector.unitVectorFromAngle(angle_range[0]*np.pi/180);
			crossProd = np.cross(vec2, vec);
			if crossProd < 0:
				angle_range[0] = Vector.getAngleBetweenPoints(scan_center, point);
			vec2 = Vector.unitVectorFromAngle(angle_range[1]*np.pi/180);
			crossProd = np.cross(vec2, vec);
			if crossProd > 0:
				angle_range[1] = Vector.getAngleBetweenPoints(scan_center, point);

		return angle_range




	def point_inside_rectangle(rect, point):
		return rect[0][0] <= point[0] and point[0] <= (rect[0][0] + rect[1][0]) and rect[0][1] <= point[1] and point[1] <= (rect[0][1] + rect[1][1]);


	def get_rectangle_angle_range(self, scan_center, rect_pos, rect_dim):
		if Radar.point_inside_rectangle([rect_pos, rect_dim], scan_center):
			return [0, 360];
		# Start by checking if the rectangle is close enough to have an intersection at all
		rect_points = [rect_pos]
		rect_points.append(rect_pos + np.array([rect_dim[0], 0]))
		rect_points.append(rect_pos + rect_dim)
		rect_points.append(rect_pos + np.array([0, rect_dim[1]]))
		rect_lines = [];
		rect_lines.append(np.array([rect_points[0], rect_points[1]]));
		rect_lines.append(np.array([rect_points[1], rect_points[2]]));
		rect_lines.append(np.array([rect_points[2], rect_points[3]]));
		rect_lines.append(np.array([rect_points[3], rect_points[0]]));

		has_inter = False;
		for i in range(4):
			rect_line = rect_lines[i];
			rect_point = rect_points[i];
			if Vector.getDistanceBetweenPoints(rect_point, scan_center) < self.radius:
				has_inter = True
				break;
			inters = circle_line_intersection(scan_center, self.radius, rect_line);
			if inters is not None and 0 < len(inters):
				has_inter = True;
				break;
		if not has_inter:
			return None;

		return self.get_rectangle_shadow_angle_range(scan_center, rect_pos, rect_dim);


	def get_dynobs_data_index_range(self, scan_center, dynobs):
		angle_range = [0, 360];
		if dynobs.shape == 1:
			angle_range = self.get_circle_angle_range(scan_center, dynobs.coordinate, dynobs.radius);
		elif dynobs.shape == 2:
			angle_range = self.get_rectangle_angle_range(scan_center, dynobs.coordinate, np.array(dynobs.size));

		if angle_range is None:
			return None;
		self.last_angrange = angle_range
		index1 = np.ceil(angle_range[0] / self._degree_step);
		index2 = min(360, np.floor(angle_range[1] / self._degree_step));
		if index2 < index1:
			index1 -= self._nPoints;
		return [int(index1), int(index2)]


	def scan_dynamic_obstacles(self, center, grid_data):
		nPoints = self._nPoints
		beams = self._beams
		radar_data = np.ones([nPoints], dtype=np.float64);
		sub_dynobs_list = [];
		for dynobs in self.env.dynamic_obstacles:
			index_range = self.get_dynobs_data_index_range(center, dynobs);
			if index_range is None:
				continue;
			for i in np.arange(index_range[0], index_range[1], 1):
				if dynobs.shape == 1:
					inters = circle_line_intersection(np.array(list(dynobs.coordinate)), dynobs.radius, [center, center+beams[i]]);
				elif dynobs.shape == 2:
					inters = Radar.rectangle_line_intersection([dynobs.coordinate, np.array(dynobs.size)], [center, center+beams[i]]);
				if len(inters) == 0:
					continue;

				inters_rel = np.array(inters) - center;
				dist = 1
				if len(inters) == 1:
					dist = Vector.magnitudeOf(inters_rel[0]);
				else:
					if np.dot(inters_rel[0], inters_rel[0]) < np.dot(inters_rel[1], inters_rel[1]):
						dist = Vector.magnitudeOf(inters_rel[0]);
					else:
						dist = Vector.magnitudeOf(inters_rel[1]);
				radar_data[i] = np.min([radar_data[i], float(dist) / float(self.radius)]);
			
		return radar_data;


	def get_dynobs_at_angle(self, center, angle):
		nPoints = self._nPoints;
		beams = self._beams;
		beam_index = np.round((angle % 360) / self._degree_step);
		min_dist = -1;
		closest_dynobs = None;
		for dynobs in self.env.dynamic_obstacles:
			if dynobs.shape == 1:
				inters = circle_line_intersection(np.array(list(dynobs.coordinate)), dynobs.radius, [center, center+beams[beam_index]]);
			elif dynobs.shape == 2:
				inters = Radar.rectangle_line_intersection([dynobs.coordinate, np.array(dynobs.size)], [center, center+beams[beam_index]]);
			if len(inters) == 0:
				continue;

			inters_rel = np.array(inters) - center;
			dist = 1
			if len(inters) == 1:
				dist = Vector.magnitudeOf(inters_rel[0]);
			else:
				if np.dot(inters_rel[0], inters_rel[0]) < np.dot(inters_rel[1], inters_rel[1]):
					dist = Vector.magnitudeOf(inters_rel[0]);
				else:
					dist = Vector.magnitudeOf(inters_rel[1]);

			if dist < min_dist or min_dist < 0:
				min_dist = dist;
				closest_dynobs = dynobs

		return closest_dynobs;


	def scan_dynamic_obstacles_old(self, center, grid_data):

		radar_data = np.ones(int(360 / int(self._degree_step)))
		currentStep = 0
		x_upper_bound = min(799, self.screen.get_width())
		y_upper_bound = min(599, self.screen.get_height())
		for degree in np.arange(0, 360, self._degree_step):
			ang_in_radians = degree * np.pi / 180
			cos_cached = np.cos(ang_in_radians)
			sin_cached = np.sin(ang_in_radians)
			for i in np.arange(0, self.radius, self.resolution):
				x = int(cos_cached * i + center[0])
				y = int(sin_cached * i + center[1])
				if ((x < 0) or (y < 0) or (x_upper_bound <= x) or (y_upper_bound <= y)):
					radar_data[currentStep] = 1
					break
				if (grid_data[x, y] & 2):
					radar_data[currentStep] = i / self.radius
					break
				#self.screen.set_at((x, y), self.beam_color)
			currentStep = currentStep + 1
		return radar_data
