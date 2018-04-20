import json
import xml.etree.ElementTree
import sys

if len(sys.argv) < 2:
	print('Need SVG filename')
	exit(1)

svg_filename = sys.argv[1]

def rect_to_poly_obs(rect):
	poly_points = []
	poly_points.append([rect['x'], rect['y']])
	poly_points.append([rect['x']+rect['width'], rect['y']])
	poly_points.append([rect['x']+rect['width'], rect['y']+rect['height']])
	poly_points.append([rect['x'], rect['y']+rect['height']])
	poly_points.append([rect['x'], rect['y']])

	return {'type': 'polygon', 'points': poly_points}

def circle_to_circle_obs(circle):
	return {'type': 'circle', 'center': circle['center'], 'radius': circle['radius']}

namespaces = {'svg': 'http://www.w3.org/2000/svg'}

e = xml.etree.ElementTree.parse(svg_filename).getroot()
all_rects = []
for atype in e.findall('.//svg:rect', namespaces):
	new_rect = dict()
	new_rect = {k: float(atype.get(k)) for k in {'x', 'y', 'width', 'height'}}
	all_rects.append(rect_to_poly_obs(new_rect))

all_circles = []
for atype in e.findall('.//svg:circle', namespaces):
	new_circle = dict()
	new_circle = {k: float(atype.get(k)) for k in {'r', 'y', 'width', 'height'}}
	new_circle['radius'] = new_circle['r']
	new_citcle['center'] = [new_citcle['x'], new_citcle['y']]
	all_circles.append(circle_to_circle_obs(new_circle))

all_obs = all_rects + all_circles


with open('{}.json'.format(svg_filename.replace('.svg', '')), 'x') as f:
	json.dump(all_obs, f, indent=4, sort_keys=True)

