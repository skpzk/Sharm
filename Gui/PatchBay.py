import numpy as np
import tkinter as tk
from State import State

from Dev.DebugUtils import cprint

COLORS = ['DeepSkyBlue2', 'DeepSkyBlue3', 'hot pink', 'gold',
'dark orange', 'firebrick2', 'forest green', 'SpringGreen2', 'goldenrod2', 'red3', 'DarkOrchid4']


implementedPatchPoints = ["VCO 1", "VCO 1 SUB", "VCO 1 PWM", "VCO 2", "VCO 2 SUB", "VCO 2 PWM", "VCO 1",
		                      "VCO 1 SUB 1", "VCO 1 SUB 2", "VCO 2", "VCO 2 SUB 1", "VCO 2 SUB 2", "CUTOFF"]


class PatchCord:
	def __init__(self, root, canvas, width, color, ID):
		self.root = root
		self.canvas = canvas

		self.id = ID

		self.started = False

		self.coordArc = [0, 0, 0, 0]
		self.arcWidth = width * 0.25

		box, start, extent = self.computeArc()

		self.color = color

		# cprint("color = ", self.color)

		self.arc = self.canvas.create_arc(box, style='arc', start=0, extent=350, width=self.arcWidth)
		self.startPoint = self.canvas.create_oval(self.coordArc, fill=self.color, outline=self.color)
		self.endPoint = self.canvas.create_oval(self.coordArc, fill=self.color, outline=self.color)

		self.canvas.itemconfig(self.arc, outline=self.color)

		self.patchPoints = []

		self.dictToSend = dict()
		self.dictToSend['type'] = 'patchbay'

	def drawPoints(self):
		xs0 = self.coordArc[0] - self.arcWidth / 2
		ys0 = self.coordArc[1] - self.arcWidth / 2
		xs1 = self.coordArc[0] + self.arcWidth / 2
		ys1 = self.coordArc[1] + self.arcWidth / 2

		self.canvas.coords(self.startPoint, [xs0, ys0, xs1, ys1])

		xe0 = self.coordArc[2] - self.arcWidth / 2
		ye0 = self.coordArc[3] - self.arcWidth / 2
		xe1 = self.coordArc[2] + self.arcWidth / 2
		ye1 = self.coordArc[3] + self.arcWidth / 2

		self.canvas.coords(self.endPoint, [xe0, ye0, xe1, ye1])

	def setStart(self, point):
		self.coordArc[:2] = point
		self.started = True
		self.draw(point)

	def draw(self, point):
		if self.started:
			self.coordArc[2:] = point
			self.canvas.itemconfig(self.arc, fill=self.color)
			box, start, extent = self.computeArc()

			self.canvas.coords(self.arc, box)
			self.canvas.itemconfig(self.arc, start=start, extent=extent)

			self.drawPoints()

	def setEnd(self, point):
		if self.started:
			self.coordArc[2:] = point
			box, start, extent = self.computeArc()

			self.canvas.coords(self.arc, box)
			self.canvas.itemconfig(self.arc, start=start, extent=extent)

			self.drawPoints()
			self.started = False

			self.connect()

	def release(self):
		self.started = False
		self.coordArc = [0, 0, 0, 0]
		self.canvas.coords(self.arc, self.coordArc)
		self.canvas.itemconfig(self.arc, fill='white')

		self.delete()

	def computeArc(self):
		a = self.coordArc[:2]
		b = self.coordArc[2:]
		center, radius = self.findCenter(a, b)
		# cprint("center = %.2f %.2f" % (center[0], center[1]))
		start, extent = self.findAngles(a, b, center)
		box = [center[0] - radius, center[1] - radius,
		       center[0] + radius, center[1] + radius]
		return box, start, extent

	def findCenter(self, a, b):
		distanceAB = distance(a, b)
		mean = (np.mean((a[0], b[0])), np.mean((a[1], b[1])))
		radius = distanceAB*.8
		distanceMeanCenter = np.sqrt(np.power(radius, 2) - np.power(distanceAB/2, 2))
		dx, dy = self.slope(a, b)
		if dx == 0:
			center = (mean[0] + distanceMeanCenter, mean[1])
		elif dy == 0:
			center = (mean[0], mean[1] - distanceMeanCenter)
		else:
			# cy is always positive, so that the cord look pulled by gravity
			cy = np.sqrt(np.power(distanceMeanCenter, 2) / (1 + np.power(dy / dx, 2)))
			cx = cy * dy / dx

			center = (mean[0] + cx, mean[1] - cy)
		return center, radius

	@staticmethod
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

	@staticmethod
	def slope(a, b):
		dx = b[0] - a[0]
		dy = b[1] - a[1]
		return dx, dy

	def delete(self):
		if len(self.patchPoints) == 2:
			self.disconnect()
		self.canvas.delete(self.arc)
		for patchPoint in self.patchPoints:
			patchPoint.connected = False
			patchPoint.patchCord = None
		self.canvas.delete(self.startPoint)
		self.canvas.delete(self.endPoint)

	def connect(self):
		# cprint("patchpoints = ", self.patchPoints)
		p1, p2 = self.patchPoints
		if p1.type == 'in':
			p1, p2 = p2, p1
			self.patchPoints = p1, p2
		d = self.dictToSend
		d['out'] = p1.title
		d['in'] = p2.title
		d['connect'] = 1
		State.events.put(State.Event("connect" + str(self.id), d))
		pass

	def disconnect(self):
		p1, p2 = self.patchPoints
		d = self.dictToSend
		d['out'] = p1.title
		d['in'] = p2.title
		d['connect'] = 0
		State.events.put(State.Event("connect" + str(self.id), d))
		pass


class PatchPoint:
	def __init__(self, root, canvas, width, position, ID, title, io):
		self.canvas = canvas

		self.ID = ID

		self.width = width

		self.x0 = position[0]
		self.y0 = position[1]

		self.center = (self.x0 + width/2, self.y0 + width/2)

		# used to detect if the mouse is on the patchPoint
		self.radius = width/2

		coordsHexa = self.computeCoordsHexa()
		coordsCircle = self.computeCoordsCircle(0.6 * width)
		coordsInnerCircle = self.computeCoordsCircle(0.4 * width)

		self.hexa = self.canvas.create_polygon(coordsHexa, fill='white', outline='black')

		self.circle = self.canvas.create_oval(coordsCircle, fill='white', outline='black')
		self.innercircle = self.canvas.create_oval(coordsInnerCircle, fill='black')

		if title not in implementedPatchPoints:
			self.canvas.itemconfig(self.circle, fill='grey')

		self.connected = False
		self.patchCord = None

		self.title = title
		self.titleLabel = self.canvas.create_text(0, 0, text=title)

		self.canvas.itemconfig(self.titleLabel,  font=("Purisa", 7))
		# widthLabel = self.canvas.winfo_width()  # I don't really know why this works  # It doesn't
		# cprint("widthLabel", widthLabel)
		#
		# heightLabel = self.canvas.winfo_height()

		self.canvas.coords(self.titleLabel, (self.center[0], coordsHexa[-1] - 9))
		# self.canvas.itemconfig(self.titleLabel, ='black')

		# test = (self.center[0], coordsHexa[-1] - 5)
		#
		# drawCross(self.canvas, test)

		# tk.Canvas.itemcget(self.titleLabel, 'width')

		self.canvas.update()

		bbox = self.canvas.bbox(self.titleLabel)

		# drawCross(self.canvas, bbox[:2])
		# drawCross(self.canvas, bbox[2:])

		if io == 'out':
			bbox = list(bbox)
			bbox[:2] = [bbox[i] - 1 for i in range(2)]
			self.canvas.create_rectangle(bbox, fill='black')
			self.canvas.itemconfig(self.titleLabel, fill='white')

		self.type = io
		self.canvas.tag_raise(self.titleLabel)

		# self.setBinds()

	def computeCoordsHexa(self):
		w = self.width
		x0, y0 = self.x0, self.y0 + w/2

		wy = w/2 * np.cos(np.pi/6)

		y1 = y2 = y0 + wy
		y4 = y5 = y0 - wy

		x1 = x5 = x0 + w/4
		x2 = x4 = x1 + w/2

		x3, y3 = x0 + self.width, y0

		return x0, y0, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5

	def computeCoordsCircle(self, circleWidth):

		width = self.width

		border = (width - circleWidth) / 2

		x0 = self.x0 + border
		y0 = self.y0 + border

		x1 = x0 + circleWidth
		y1 = y0 + circleWidth

		return x0, y0, x1, y1


class PatchBay:
	def __init__(self, root):
		self.root = root
		# self.initRoot()
		# self.back = back
		# self.root.update()
		# self.initBack()

		widthCanvas = 260
		heightCanvas = 568

		self.canvas = tk.Canvas(root)
		self.canvas.config(width=widthCanvas, height=heightCanvas, borderwidth=0, highlightthickness=0, bg="white")
		self.canvas.place(x=580 + 25, y=15)

		self.setBinds()

		self.widthPatchPoint = 36

		width = self.widthPatchPoint
		position1 = [0.05*widthCanvas, widthCanvas/2 - width/2]
		position2 = [widthCanvas - 0.05*widthCanvas - width, widthCanvas/2 - width/2]

		gridX = 4
		gridY = 8

		borderX = 30
		borderY = 25

		widthGridX = gridX * (width + borderX) + borderX
		widthGridY = gridY * (width + borderY) + borderY

		x0 = (widthCanvas - widthGridX) / 2 + borderX
		y0 = (heightCanvas - widthGridY) / 2 + borderY

		position = [position1, position2]

		titlesIn = ["VCO 1", "VCO 1 SUB", "VCO 1 PWM", "VCA", "VCO 2", "VCO 2 SUB", "VCO 2 PWM", "CUTOFF", "PLAY"]
		titlesIn.extend(["RESET", "TRIGGER", "RHYTHM 1", "RHYTHM 2", "RHYTHM 3", "RHYTHM 4", "UNDEF", "CLOCK"])

		titlesOut = ["VCA", "VCO 1", "VCO 1 SUB 1", "VCO 1 SUB 2", "VCA EG", "VCO 2", "VCO 2 SUB 1", "VCO 2 SUB 2"]
		titlesOut.extend(["VCF EG", "SEQ 1", "SEQ 1 CLK", "SEQ 2", "SEQ 2 CLK", "CLOCK", "TRIGGER"])

		titlesIndex = [3, 4, 4, 4, 4, 1, 4, 4, 2, 2]

		titles = []
		types = []

		for i in range(int(len(titlesIndex)/2)):
			for j in range(titlesIndex[2*i]):
				titles.append(titlesIn.pop(0))
				types.append('in')
			for j in range(titlesIndex[2*i+1]):
				titles.append(titlesOut.pop(0))
				types.append('out')

		# cprint(titles)

		self.patchpoints = []
		for i in range(gridY):
			for j in range(gridX):
				x = x0 + j * (width + borderX)
				y = y0 + i * (width + borderY)
				ID = j + i*gridX
				self.patchpoints.append(PatchPoint(self.root, self.canvas, width, (x, y), ID, titles[ID], types[ID]))

		self.patchCords = []
		self.activePatchCordID = None

		self.colors = COLORS.copy()

		# Create section title

		titleID = self.canvas.create_text(widthCanvas/2, 10, text='Patchbay')
		self.canvas.itemconfig(titleID, font=("Purisa", 8))
		bbox = self.canvas.bbox(titleID)
		bbox = [bbox[0] - 1, bbox[1] - 1, bbox[2], bbox[3]]

		self.canvas.create_line(0, 10, bbox[0] - 3, 10)
		self.canvas.create_line(bbox[2] + 3, 10, widthCanvas, 10)

		self.canvas.create_rectangle(bbox, fill='black')
		self.canvas.itemconfig(titleID, fill='white')
		self.canvas.tag_raise(titleID)

		# create in/out hint
		inoutY = self.patchpoints[-1].center[1] + 40
		inoutID = self.canvas.create_text(widthCanvas / 2, inoutY, text='In / Out')
		self.canvas.itemconfig(inoutID, font=("Purisa", 7))
		inoutbbox = self.canvas.bbox(inoutID)
		outID = self.canvas.create_text(widthCanvas / 2, inoutY, text='Out')
		self.canvas.itemconfig(outID, font=("Purisa", 7))
		outbbox = self.canvas.bbox(outID)
		outWidth = outbbox[2] - outbbox[0]
		self.canvas.coords(outID, [inoutbbox[2] - outWidth/2 - 1, inoutY])
		newoutbbox = self.canvas.bbox(outID)
		newoutbbox = [newoutbbox[0] - 1, newoutbbox[1] - 1, newoutbbox[2], newoutbbox[3]]
		self.canvas.create_rectangle(newoutbbox, fill='black')
		self.canvas.itemconfig(outID, fill='white')
		self.canvas.tag_raise(outID)


	def setBinds(self):
		self.canvas.bind('<1>', self.setLineStartingPoint)
		self.canvas.bind("<B1-Motion>", self.drawLine)
		self.canvas.bind("<ButtonRelease-1>", self.attachLine)

	def setLineStartingPoint(self, posn):
		cx = posn.x
		cy = posn.y

		center, patchPoint = self.findPatchPoint(cx, cy)

		if center:
			if patchPoint.connected:
				self.patchCords.pop(self.patchCords.index(patchPoint.patchCord))
				patchPoint.patchCord.delete()


			color = self.findColor()

			ID = len(self.patchCords)
			patchCord = PatchCord(self.root, self.canvas, self.widthPatchPoint, color, ID)

			patchCord.patchPoints.append(patchPoint)
			patchPoint.patchCord = patchCord
			patchPoint.connected = True


			# cprint(ID)

			self.activePatchCordID = ID

			# cprint(self.activePatchCordID)

			self.patchCords.append(patchCord)
			self.patchCords[ID].setStart(center)

	def drawLine(self, posn):
		cx = posn.x
		cy = posn.y
		# self.b = (cx, cy)
		# self.drawArc()
		# cprint(self.activePatchCordID)
		if self.activePatchCordID is not None:
			# cprint("True")

			self.patchCords[self.activePatchCordID].draw((cx, cy))

	def findPatchPoint(self, cx, cy):
		for patchpoint in self.patchpoints:
			if distance((cx, cy), patchpoint.center) < patchpoint.radius:
				return patchpoint.center, patchpoint
		# cprint("Not found")
		return None, None

	def attachLine(self, posn):
		cx = posn.x
		cy = posn.y

		center, patchPoint = self.findPatchPoint(cx, cy)
		if self.activePatchCordID is not None:
			if center and patchPoint.type != self.patchCords[self.activePatchCordID].patchPoints[0].type:
				# ie if the mouse is on a patchpoint and there is an in and an out patchpoint
				if patchPoint.title in implementedPatchPoints and self.patchCords[self.activePatchCordID].patchPoints[0].title in implementedPatchPoints:
					# ie if the function linked to both patchpoints are implemented
					if patchPoint.connected:
						# if patchPoint is already connected, destroy previous connection
						tmp = self.patchCords[self.activePatchCordID]
						index = self.patchCords.index(patchPoint.patchCord)

						self.patchCords.pop(index)

						patchPoint.patchCord.delete()
						if index == self.activePatchCordID:
							return 0

						self.activePatchCordID = self.patchCords.index(tmp)

					patchPoint.patchCord = self.patchCords[-1]
					patchPoint.connected = True
					self.patchCords[self.activePatchCordID].patchPoints.append(patchPoint)
					self.patchCords[self.activePatchCordID].setEnd(center)
					# cprint("Patchpoint départ  :", self.patchCords[self.activePatchCordID].patchPoints[0].title)
					# cprint("Patchpoint arrivée :", self.patchCords[self.activePatchCordID].patchPoints[1].title)
					"""
						p1 = self.patchCords[self.activePatchCordID].patchPoints[0]
						p2 = self.patchCords[self.activePatchCordID].patchPoints[1]
						connection is made by the setEnd method"""
				else:
					cprint("not implemented yet")
					self.abortPatchCord()
			else:
				self.abortPatchCord()
			self.activePatchCordID = None

	def abortPatchCord(self):
		self.patchCords[self.activePatchCordID].release()
		self.patchCords.pop(self.patchCords.index(self.patchCords[self.activePatchCordID]))

	def findColor(self):
		if len(self.colors) <= 0:
			self.colors = COLORS.copy()

		color = self.colors.pop(np.random.randint(len(self.colors)))
		return color

	def connect(self, titleout, titlein):
		# called only at state init
		p1 = []
		p2 = []
		for p in self.patchpoints:
			if p.title == titleout and p.type == 'out':
				p1 = p
			if p.title == titlein and p.type == 'in':
				p2 = p

		if (not p1) or (not p2):
			cprint("patchpoint does not exist")
			return -1

		if p1.connected or p2.connected:
			cprint("already connected")
			return -1

		ID = len(self.patchCords)
		color = self.findColor()
		patchCord = PatchCord(self.root, self.canvas, self.widthPatchPoint, color, ID)

		patchCord.patchPoints.append(p1)
		patchCord.setStart(p1.center)
		p1.patchCord = patchCord
		p1.connected = True

		self.activePatchCordID = ID

		p2.patchCord = patchCord
		p2.connected = True
		patchCord.patchPoints.append(p2)
		patchCord.setEnd(p2.center)

		self.patchCords.append(patchCord)

	def quit_root(self, _):
		self.root.quit()


def distance(a, b):
	return np.sqrt(np.power(a[0] - b[0], 2) + np.power(a[1] - b[1], 2))


def drawCross(canvas, test):
	canvas.create_line(test[0] - 15, test[1], test[0] + 15, test[1], fill='red')
	canvas.create_line(test[0], test[1] - 15, test[0], test[1] + 15, fill='red')


if __name__ == "__main__":
	root = tk.Tk()
	root.geometry("900x600")
	back = tk.Frame(root)
	back.pack_propagate(0)
	back.pack(fill=tk.BOTH, expand=1)
	gui = PatchBay(root)

	root.mainloop()
