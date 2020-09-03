import numpy as np
import tkinter as tk

from State import State
from Gui import DrawUtils


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
		self.dictToSend['buttontype'] = 'wavebutton'
		self.dictToSend['type'] = 'button'

		self.coordsRect.extend([position[0] + width, position[1] + self.nbPositions * width])
		self.rect = self.canvas.create_rectangle(self.coordsRect, fill='white', outline='black')

		self.state = 0

		self.widthButton = .6*width
		self.coordsButton = [0, 0, 0, 0]
		self.button = self.canvas.create_rectangle(self.coordsButton, fill='black', outline='black')

		self.stateList = ['tri', 'sqr', 'sine']

		self.redrawState()

		self.inMotion = False
		self.cursorOnState = False

		self.drawWaves()

		self.setBinds()

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
		State.events.put(State.Event('wave', self.dictToSend))
		# cprint("State = ", self.state)
		self.redrawState()

	def buttonRelease(self, posn):
		if not self.inMotion:
			i = self.findCenter(posn)
			if not isinstance(i, list):
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
			return posy - s
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


class MainFrame:
	def __init__(self, root):
		self.root = root
		self.initRoot()
		self.back = tk.Frame(master=self.root)
		# self.root.update()
		self.initBack()

		widthCanvas = 400
		heightCanvas = 600

		self.canvas = tk.Canvas(root)
		self.canvas.config(width=widthCanvas, height=heightCanvas, borderwidth=0, highlightthickness=0, bg="white")
		self.canvas.place(x=200, y=0)

		button = WaveSelect(self.canvas, 8, [150, 100], 1, 0)

	def initRoot(self):
		self.root.title('Patchbay')
		self.root.geometry("800x600")

	def initBack(self):
		self.back.pack_propagate(0)
		self.back.pack(fill=tk.BOTH, expand=1)
		self.back.bind("<KeyPress-q>", self.quit_root)
		self.back.bind("<Destroy>", self.quit_root)

		self.back.focus_set()

	def quit_root(self, _):
		self.root.quit()


class RythmButton:
	def __init__(self, back, width, height, position, seqID, clkID):
		self.back = back
		self.seqID = seqID
		self.clkID = clkID
		self.canvas = tk.Canvas(self.back, width=width, height=height, highlightthickness=0)
		self.canvas.place(x=position[0], y=position[1], width=width, height=height)
		self.button = tk.Button(self.canvas, text="Seq" + str(seqID),
		                        bg='white', activebackground='white',
		                        activeforeground='black', highlightthickness=1, relief=tk.FLAT)
		self.button.config(font=("Purisa", 8))
		# cprint(self.button)
		# self.canvas.itemconfig(self.button, font=("Purisa", 4))

		i = clkID - 1
		j = seqID - 1

		self.ID = i * 2 + j
		# self.button = tk.Button(self.canvas, text=str(ID))
		self.button.pack()
		self.state = 1

		self.dictToSend = dict([('buttonid', self.ID), ('clkid', self.clkID), ('seqid', self.seqID), ('state', self.state)])
		self.dictToSend['type'] = 'button'
		self.dictToSend['buttontype'] = 'rythmbutton'
		self.dictToSend['state'] = self.state

	def toggle(self, state=None):
		if state:
			self.state = - state + 1
		if self.state == 1:
			# self.button.config(relief=tk.SUNKEN)
			self.button.config(bg='black')
			self.button.config(fg='white')
			self.button.config(activebackground='grey')
			self.button.config(activeforeground='black')
			self.state = 0
			self.dictToSend['state'] = self.state
			State.events.put(State.Event('callbackClk' + str(self.seqID) + str(self.clkID), self.dictToSend))
		else:
			# self.button.config(relief=tk.RAISED)
			self.button.config(bg='white')
			self.button.config(fg='black')
			self.button.config(activebackground='grey')
			self.button.config(activeforeground='black')
			self.state = 1
			self.dictToSend['state'] = self.state
			State.events.put(State.Event('callbackClk' + str(self.seqID) + str(self.clkID), self.dictToSend))


class VcoButton:
	def __init__(self, canvas, width, height, position, ID, voiceID, titles):
		self.canvas = canvas
		self.button = tk.Button(self.canvas, text=titles[ID].capitalize(),
		                        bg='white', activebackground='white',
		                        activeforeground='black', highlightthickness=1, relief=tk.FLAT)
		# canvas.itemconfigure(self.button, text='test')

		self.button.place(x=position[0], y=position[1], width=width, height=height)
		self.button.config(font=("Purisa", 8))

		self.ID = ID
		self.voiceID = voiceID
		self.title = titles[ID]
		if ID < 3:
			self.seqID = 1
		else:
			self.seqID = 2
		self.state = 1

		self.dictToSend = dict([('seqid', self.seqID), ('id', self.ID), ('voiceid', self.voiceID), ('state', self.state)])
		self.dictToSend['type'] = 'button'
		self.dictToSend['buttontype'] = 'vcobutton'
		self.dictToSend['state'] = self.state

	# self.vcoEvent = VcoEvent(self.seqID, self.ID, self.state)

	def toggle(self, state=None):
		if state:
			self.state = - state + 1
		if self.state == 1:
			# self.button.config(relief=tk.SUNKEN)
			self.button.config(bg='black')
			self.button.config(fg='white')
			self.button.config(activebackground='grey')
			self.button.config(activeforeground='black')
			self.state = 0
			# self.vcoEvent.state = 0
			# State.events.put(State.Event('Seq' + str(self.seqID) + "Assign", self.title + str(self.state)))
			self.dictToSend['state'] = self.state
			State.events.put(State.Event('assign' + str(self.seqID) + str(self.ID), self.dictToSend))

		else:
			# self.button.config(relief=tk.RAISED)
			self.button.config(bg='white')
			self.button.config(fg='black')
			self.button.config(activebackground='grey')
			self.button.config(activeforeground='black')
			self.state = 1
			# self.vcoEvent.state = 0
			# State.events.put(State.Event('Seq' + str(self.seqID) + "Assign", self.title + str(self.state)))
			self.dictToSend['state'] = self.state
			State.events.put(State.Event('assign' + str(self.seqID) + str(self.ID), self.dictToSend))


class Rotary:
	def __init__(self, back, width, position, ID, gui, title=""):
		self.linewidth = 1
		self.width = width
		self.gui = gui

		coord = 10, 0, width+10, width
		coord = [i + self.linewidth for i in coord]

		width_c = width + 2*self.linewidth

		self.ID = ID
		self.title = title
		self.param = title

		self.arc_extent = 280  # should not be more than 359
		self.arc_start = -(self.arc_extent-180)//2

		self.back = back

		height_c = width_c
		width_c = width_c+20

		self.canvas = tk.Canvas(back, width=width_c, height=height_c + 20, highlightthickness=0)
		self.canvas.place(x=position[0], y=position[1], width=width_c, height=height_c + 20)
		# self.canvas.config(bg='DeepSkyBlue1')
		self.canvas.config(bg='white')

		self.coord_arc = coord
		self.r = (coord[2] - coord[0]) / 2
		self.center = (coord[0] + coord[2]) / 2, (coord[1] + coord[3]) / 2
		self.centerAbs = (position[0] + self.center[0], position[1] + self.center[1])
		self.arc = self.canvas.create_arc(coord, start=self.arc_start, extent=self.arc_extent, fill="", style='arc', width=2)#self.linewidth)
		self.coord_line = 2 * self.center
		self.line = self.canvas.create_line(self.coord_line, width=self.linewidth, capstyle='round')
		self.titleLabel = self.canvas.create_text(self.center[0], coord[3]+5, text=title)
		self.canvas.itemconfig(self.titleLabel, font=("Purisa", 8))
		self.label = self.canvas.create_text(self.center[0], coord[3]+17, text=0)
		self.canvas.itemconfig(self.label, font=("Purisa", 7))

		self.alpha = 0
		self.alpha_deg = 0
		self.value = 0
		self.valueMax = 127.
		self.valueMin = 0
		self.valuesTablePrompt = [str(i) for i in range(int(self.valueMax)+1)]
		self.valuesTableSend = [i for i in range(int(self.valueMax)+1)]
		self.dictToSend = dict()
		self.dictToSend['type'] = 'rot'
		self.dictToSend['rottype'] = 'generic'
		self.dictToSend['messagetype'] = 'undef'
		self.computeAlphaFromAlphadeg()
		self.redraw_line()
		self.cursorOn = False
		self.cursorOnTitle = False
		self.cx = self.cy = 0

		self.muted = False
		self.unmuteValue = 0

		self.setBinds()

		# self.canvas.pack()

		coords = DrawUtils.computeCoordsCircle(self.r * 1.5, self.center)

		self.oval = self.canvas.create_oval(coords)

	def valueToSend(self):
		self.dictToSend['value'] = self.valuesTableSend[int(self.value)]
		return self.dictToSend

	def redraw_line(self):
		lx = self.r * np.cos(self.alpha) + self.center[0]
		ly = self.r * np.sin(-self.alpha) + self.center[1]
		self.coord_line = lx, ly, self.center[0], self.center[1]

		self.canvas.coords(self.line, self.coord_line)

	def cursor_on_rotary(self):
		if np.sqrt(np.power(self.cx - self.center[0], 2) + np.power(self.cy - self.center[1], 2)) < self.r:
			self.cursorOn = True
		else:
			self.cursorOn = False
		if (-25 < (self.cx - self.center[0]) < 25) and (0 < (self.cy - self.coord_arc[3]) < 20):
			self.cursorOnTitle = True
			# print("On Title")
		else:
			self.cursorOnTitle = False

	def test(self, posn):
		self.cx = posn.x
		self.cy = posn.y
		if self.title == "Clk2":
			x = self.cx - self.center[0]
			y = self.cy - self.coord_arc[3]
			print("x = ", x, "y = ", y)

	def setValue(self, value, sendMidiEvent=False):
		# print("Gui : Value = ", value)
		self.value = self.valuesTableSend.index(value)

		self.alpha_deg = np.round(self.value*280 / self.valueMax)

		self.computeAlphaFromAlphadeg()

		self.redraw_line()
		self.canvas.itemconfigure(self.label, text=self.valuesTablePrompt[int(self.value)])
		if sendMidiEvent:
			State.events.put(State.Event(self.param, self.valueToSend()))

	def computeAlphaFromAlphadeg(self):
		self.alpha = (360 - self.alpha_deg - (180+self.arc_start)) * np.pi / 180.

	def computeAlphaFromCursor(self):
		alpha = np.arctan2(-self.cy + self.center[0], self.cx - self.center[0])
		alpha_deg = int(alpha * 180 / np.pi)
		alpha_deg = 360 - np.mod(alpha_deg - (self.arc_extent+self.arc_start), 360)
		# self.cursorOnTitle = False
		if alpha_deg > (180+self.arc_extent/2):
			# self.cursorOnTitle = True
			alpha_deg = 0
		elif alpha_deg >= self.arc_extent:
			# self.cursorOnTitle = True
			alpha_deg = self.arc_extent

		# discrete rotation adapted to max value :
		value = np.round(alpha_deg * self.valueMax / 280.)
		alpha_deg = np.round(value*280 / self.valueMax)

		self.alpha_deg = alpha_deg
		self.computeAlphaFromAlphadeg()

	def updateValue(self):
		# print(self.value)
		self.value = np.round(self.value * self.valueMax / 280.)
		# cprint("value = ", self.value)
		# self.value = self.value * (self.value < self.valueMax) + (self.valueMax)*(self.value >= self.valueMax)
		self.canvas.itemconfigure(self.label, text=self.valuesTablePrompt[int(self.value)])
		State.events.put(State.Event(self.param, self.valueToSend()))

	def bind(self, posn):
		self.cx = posn.x
		self.cy = posn.y
		if self.cursorOn:
			self.canvas.itemconfigure(self.label, fill='red')
			self.canvas.focus_set()
			self.computeAlphaFromCursor()
			self.redraw_line()
			self.value = self.alpha_deg
			self.updateValue()
			# self.canvas.itemconfigure(self.label, text=value)

	def bindPressed(self, posn):
		self.bindB1(posn, True)

	def bindReleased(self, posn):
		self.bindB1(posn, False)

	def bindB1(self, posn, pressed):
		self.cx = posn.x
		self.cy = posn.y
		self.cursor_on_rotary()
		if self.cursorOnTitle:
			self.canvas.itemconfigure(self.label, fill='red')
			self.canvas.focus_set()
		elif self.cursorOn:
			# print("On")
			self.canvas.itemconfigure(self.label, fill='red')
			self.canvas.focus_set()
			if pressed:
				self.computeAlphaFromCursor()
				self.redraw_line()
				self.value = self.alpha_deg
				# self.canvas.itemconfigure(self.label, text=value)
				self.updateValue()
		else:
			# print("Here")
			self.canvas.itemconfigure(self.label, fill='black')
			self.back.focus()

	def bindArrowKey(self, direction):
		self.cursor_on_rotary()
		if self.cursorOn or self.canvas.focus_get():
			alpha_deg = self.alpha_deg + direction * self.arc_extent / self.valueMax
			alpha_deg = (alpha_deg >= self.arc_extent) * self.arc_extent + (alpha_deg < self.arc_extent) * alpha_deg
			alpha_deg = (alpha_deg > 0) * alpha_deg
			self.alpha_deg = alpha_deg
			self.computeAlphaFromAlphadeg()
			self.redraw_line()
			self.value = self.alpha_deg
			# self.canvas.itemconfigure(self.label, text=value)
			self.updateValue()

	def bindUp(self, _):
		self.bindArrowKey(1)

	def bindDown(self, _):
		self.bindArrowKey(-1)

	def setBinds(self):
		self.canvas.bind("<B1-Motion>", self.bind)
		self.canvas.bind("<1>", self.bindPressed)
		self.canvas.bind("<Up>", self.bindUp)
		self.canvas.bind("<Right>", self.bindUp)
		self.canvas.bind("<Down>", self.bindDown)
		self.canvas.bind("<Left>", self.bindDown)
		self.canvas.bind("<ButtonRelease-1>", self.bindReleased)
		# self.canvas.bind("<Motion>", self.gui.updatePos)
		self.canvas.bind("<FocusOut>", self.focusOut)
		self.canvas.bind("<Escape>", self.focusOut)
		self.canvas.bind("<KeyPress-q>", self.focusOut)
		self.canvas.bind("<KeyPress-m>", self.mute)
		self.canvas.bind("<FocusIn>", self.focusIn)

	def setTitle(self, title):
		self.title = title
		self.canvas.itemconfigure(self.titleLabel, text=title)

	def focusOut(self, _):
		if self.canvas.focus_get():
			self.back.focus()
		self.canvas.itemconfigure(self.label, fill='black')

	def focusIn(self, _):
		self.canvas.itemconfigure(self.label, fill='red')

	def mute(self, _):
		if ('level' in self.title) or ('Vol' in self.title):
			if self.muted:
				self.setValue(self.unmuteValue, True)
				self.muted = False
			else:
				self.unmuteValue = self.value
				self.setValue(0, True)
				self.muted = True

	def noteOn(self):
		self.canvas.itemconfigure(self.label, fill='orange')

	def noteOff(self):
		self.canvas.itemconfigure(self.label, fill='black')
