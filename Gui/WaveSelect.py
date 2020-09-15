import numpy as np

from State import State
# from Dev.DebugUtils import *


class WaveSelect:
	def __init__(self, canvas, width, position, orientation, ID):
		self.canvas = canvas
		self.width = width
		self.coordsRect = position

		self.orientation = orientation

		self.nbPositions = 3

		self.ID = ID

		voicesID = [[0, 2, 3], [1, 4, 5]]

		self.voicesID = voicesID[self.ID]

		self.dictToSend = dict()
		self.dictToSend['id'] = ID
		self.dictToSend['v0'] = self.voicesID[0]
		self.dictToSend['v1'] = self.voicesID[1]
		self.dictToSend['v2'] = self.voicesID[2]
		self.dictToSend['wave'] = 'sine'
		self.dictToSend['buttontype'] = 'wave'
		self.dictToSend['type'] = 'button'

		self.coordsRect.extend([position[0] + width, position[1] + self.nbPositions * width])
		self.rect = self.canvas.create_rectangle(self.coordsRect, fill='white', outline='black')
		self.state = 0

		self.widthButton = .6*width
		self.coordsButton = [0, 0, 0, 0]
		self.button = self.canvas.create_rectangle(self.coordsButton, fill='black', outline='black')

		self.stateList = ['tri', 'sqr', 'saw']
		self.eventName = 'wave' + str(self.ID)

		self.redrawState()

		self.inMotion = False
		self.cursorOnState = False

		self.drawWaves()

		self.setBinds()

	def updateSizeValues(self):
		coord = self.canvas.coords(self.rect)
		self.coordsRect = coord
		self.width = coord[2] - coord[0]
		self.widthButton = .6 * self.width

	def drawWaves(self):
		# triangle
		x = self.coordsRect[0] + (self.orientation == -1) * (2 * self.width + 1)
		y = self.coordsRect[1]
		pos = [x - .8 * self.width,
		       y + .7 * self.width,
		       x - .5 * self.width,
		       y + .3 * self.width,
		       x - .2 * self.width,
		       y + .7 * self.width,
		       x - .1 * self.width,
		       y + .5 * self.width]
		self.canvas.create_line(pos[:4], fill='black')
		self.canvas.create_line(pos[2:6], fill='black')
		# self.canvas.create_line(pos[4:], fill='black')

		# square
		y = self.coordsRect[1] + self.width
		pos = [x - .9 * self.width,
		       y + .8 * self.width,
		       x - .85 * self.width,
		       y + .8 * self.width,
		       x - .85 * self.width,
		       y + .2 * self.width,
		       x - .2 * self.width,
		       y + .2 * self.width,
		       x - .2 * self.width,
		       y + .8 * self.width]
		self.canvas.create_line(pos[:4], fill='black')
		self.canvas.create_line(pos[2:6], fill='black')
		self.canvas.create_line(pos[4:], fill='black')

		# sawtooth
		y = self.coordsRect[1] + 2 * self.width
		pos = [x - .9 * self.width,
		       y + .8 * self.width,
		       x - .9 * self.width,
		       y + .2 * self.width,
		       x - .2 * self.width,
		       y + .8 * self.width]
		self.canvas.create_line(pos[:4], fill='black')
		self.canvas.create_line(pos[2:6], fill='black')
		# self.canvas.create_line(pos[4:], fill='black')

	def redrawState(self):

		x = self.coordsRect[0]
		y = self.coordsRect[1]
		s = self.state
		w = self.width
		wB = self.widthButton
		dW = (w - wB) / 2
		self.coordsButton[0] = x + dW
		self.coordsButton[1] = y + s * w + dW
		self.coordsButton[2] = x + w - dW
		self.coordsButton[3] = y + (s + 1) * w - dW
		self.canvas.coords(self.button, self.coordsButton)

	def updateState(self, i):
		# cprint("Here")
		self.state = np.mod(self.state + i, self.nbPositions)
		self.dictToSend['wave'] = self.stateList[self.state]
		State.events.put(State.Event(self.eventName, self.dictToSend))
		# cprint("State = ", self.state)
		self.redrawState()

	def buttonRelease(self, posn):
		if not self.inMotion:
			i = self.findCenter(posn)
			if i:
				self.updateState(1)
		self.inMotion = False
		self.cursorOnState = False

	def findCenter(self, posn):
		s = self.state
		x = posn.x
		y = posn.y

		posx = (x - self.coordsRect[0]) / self.width
		posy = (y - self.coordsRect[1]) // self.width

		if (0 <= posx <= 1) and (0 <= posy < self.nbPositions):
			return int(posy - s)
		return []

	def buttonPress(self, posn):
		# cprint("Working")
		self.cursorOnState = self.onState(posn)

	def onState(self, posn):
		x = posn.x
		y = posn.y
		if self.coordsButton[0] < x < self.coordsButton[2]:
			if self.coordsButton[1] < y < self.coordsButton[3]:
				return True
		return False

	def motion(self, posn):
		if self.cursorOnState:
			i = self.findCenter(posn)
			self.inMotion = True
			if i:
				self.updateState(i)

	def setBinds(self):
		self.canvas.bind('<1>', self.buttonPress)
		self.canvas.bind("<B1-Motion>", self.motion)
		self.canvas.bind("<ButtonRelease-1>", self.buttonRelease)

	def toggle(self, wave):
		# print("toogled")
		self.updateState(self.stateList.index(wave))
