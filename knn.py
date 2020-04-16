import math
import xml.etree.ElementTree as et

def extract_point(circle):
	return (float(circle.attrib['cx']), float(circle.attrib['cy']))

def get_points_and_target_from_svg(svg_filename):
	tree = et.parse(svg_filename)

	points = [extract_point(circle) for circle in tree.iter('{http://www.w3.org/2000/svg}circle')
				if 'id' in circle.attrib 
				if circle.attrib['id'] != 'pivot']

	target = [extract_point(circle) for circle in tree.iter('{http://www.w3.org/2000/svg}circle')
				if 'id' in circle.attrib 
				if circle.attrib['id'] == 'pivot']

	return points, target

def distance(p1, p2):
	x1, y1 = p1
	x2, y2 = p2

	dx = x2 - x1
	dy = y2 - y1

	return math.sqrt(dx * dx + dy * dy)

def knn(points, target):
	best_point = None
	best_distance = None

	for point in points:
		dist = distance(point, target)
		if best_distance is None or dist < best_distance:
			best_distance = dist
			best_point = point
	
	return best_point, best_distance

def build_kd_tree(points, depth = 0):
	n = len(points)

	if n == 1:
		return points[0]

	k = len(points[0])	
	axis = depth % k
	
	psorted = sorted(points, key = lambda point: point[axis])

	return {
			'head'  : (axis, psorted[n / 2][axis]),
			'left'  : build_kd_tree(psorted[: n / 2], depth + 1),
			'right' : build_kd_tree(psorted[n / 2 :], depth + 1)
		}

maxDim = []
minDim = []

def kd_tree_check_node(kd_node, target, current_best_point, current_best_distance):
	b = False
	if type(kd_node) is tuple:
		d = distance(target, kd_node)
		if d < current_best_distance:
			return d, kd_node, True
	else:
		axis = kd_node['head'][0]
		if kd_node['head'][1] < maxDim[axis]:
			# check the right node
			current_best_distance, current_best_point, b = kd_tree_check_node(kd_node['right'], target, 
				current_best_point, current_best_distance)
		if kd_node['head'][1] > minDim[axis]:
			# check the left node
			current_best_distance, current_best_point, b = kd_tree_check_node(kd_node['left'], target, 
				current_best_point, current_best_distance)
	
	return current_best_distance, current_best_point, b

def kd_tree_search(kd_tree, target):
	if type(kd_tree) is tuple:
		return distance(kd_tree, target), kd_tree, True
	else:
		if target[kd_tree['head'][0]] <= kd_tree['head'][1]:			
			direction = 'left'
			opp_dir = 'right'
		else:
			direction = 'right'
			opp_dir = 'left'
	
	dist, point, d = kd_tree_search(kd_tree[direction], target)

	if d:
		global maxDim 
		maxDim = [target[i] + dist for i in range(len(point))]
		global minDim 
		minDim = [target[i] - dist for i in range(len(point))]

	if opp_dir == 'right' and kd_tree['head'][1] > maxDim[kd_tree['head'][0]]:
			return dist, point, False
	elif opp_dir == 'left' and kd_tree['head'][1] < minDim[kd_tree['head'][0]]:
			return dist, point, False
	else:
		return kd_tree_check_node(kd_tree[opp_dir], target, point, dist)

def kd_tree_nn(kd_tree, target):
	dist, point, d = kd_tree_search(kd_tree, target)
	print(dist, point)
	return dist, point

points, [target] = get_points_and_target_from_svg("points.svg")
kd_tree = build_kd_tree(points)
print(kd_tree)
dist, point = kd_tree_nn(kd_tree, target)
