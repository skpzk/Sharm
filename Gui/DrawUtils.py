import numpy as np


def computeArc(a, b, direction='patchcord'):
	center, radius = findCenter(a, b, direction)
	# cprint("center = %.2f %.2f" % (center[0], center[1]))
	start, extent = findAngles(a, b, center)
	box = [center[0] - radius, center[1] - radius,
	       center[0] + radius, center[1] + radius]
	return box, start, extent


def findAngles(a, b, c):
	start = np.arctan2(- a[1] + c[1], a[0] - c[0])
	start = start * 180 / np.pi
	stop = np.arctan2(- b[1] + c[1], b[0] - c[0])
	stop = stop * 180 / np.pi
	extent = stop-start
	if extent < -180:
		extent += 360
	elif extent > 180:
		extent -= 360
	return start, extent


def slope(a, b):
	dx = b[0] - a[0]
	dy = b[1] - a[1]
	return dx, dy


def findCenter(a, b, direction='patchcord'):
	distanceAB = distance(a, b)
	mean = (np.mean((a[0], b[0])), np.mean((a[1], b[1])))
	radius = distanceAB*.8
	distanceMeanCenter = np.sqrt(np.power(radius, 2) - np.power(distanceAB/2, 2))
	dx, dy = slope(a, b)
	if direction == 'patchcord':
		if dx == 0:
			center = (mean[0] + distanceMeanCenter, mean[1])
		elif dy == 0:
			center = (mean[0], mean[1] - distanceMeanCenter)
		else:
			# cy is always positive, so that the cord look pulled by gravity
			cy = np.sqrt(np.power(distanceMeanCenter, 2) / (1 + np.power(dy / dx, 2)))
			cx = cy * dy / dx

			center = (mean[0] + cx, mean[1] - cy)
	else:
		if direction == 'up':
			d = 1
		else:
			d = -1

		if dx == 0:
			center = (mean[0] + distanceMeanCenter * d, mean[1])
		elif dy == 0:
			center = (mean[0], mean[1] - distanceMeanCenter * d)
		else:
			# cy is always positive, so that the cord look pulled by gravity
			cy = d * np.sqrt(np.power(distanceMeanCenter, 2) / (1 + np.power(dy / dx, 2)))
			cx = cy * dy / dx

			center = (mean[0] + cx, mean[1] - cy)
	return center, radius


def distance(a, b):
	return np.sqrt(np.power(a[0] - b[0], 2) + np.power(a[1] - b[1], 2))


def drawCross(canvas, test):
	canvas.create_line(test[0] - 15, test[1], test[0] + 15, test[1], fill='red')
	canvas.create_line(test[0], test[1] - 15, test[0], test[1] + 15, fill='red')


def computeCoordsHexa(width, x, y):
	w = width
	x0, y0 = x, y + w/2

	wy = w/2 * np.cos(np.pi/6)

	y1 = y2 = y0 + wy
	y4 = y5 = y0 - wy

	x1 = x5 = x0 + w/4
	x2 = x4 = x1 + w/2

	x3, y3 = x0 + w, y0

	return x0, y0, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5


def computeCoordsCircle(width, center):

	x, y = center

	r = width / 2

	x0 = x - r
	y0 = y - r

	x1 = x + r
	y1 = y + r

	return x0, y0, x1, y1
