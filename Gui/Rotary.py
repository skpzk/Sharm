import tkinter as tk
import numpy as np
import queue

from State import State
from Gui import DrawUtils
from Gui.ResizingCanvas import ResizingCanvas
from Gui import Gui


class Rotary:
	"""
	Mimics a rotary knob
	"""
	def __init__(self, back, rel, ID, title=""):

		# identification parameters
		self.ID = ID
		self.title = title
		self.param = title

		# values dictionary to send to State
		self.dictToSend = dict()
		self.dictToSend['type'] = 'rot'
		self.dictToSend['rottype'] = 'generic'
		self.dictToSend['messagetype'] = 'undef'

		# Mute parameters
		self.muted = False
		self.unmuteValue = 0

		# Value of the knob
		self.value = 0
		self.valueMax = 127.
		self.valueMin = 0
		self.valuesTablePrompt = [str(i) for i in range(int(self.valueMax) + 1)]
		self.valuesTableSend = [i for i in range(int(self.valueMax) + 1)]

		# arc parameters
		self.alpha = 0
		self.alpha_deg = 0
		self.arc_extent = 280  # should not be more than 359
		self.arc_start = -(self.arc_extent - 180) // 2

		self.back = back
		self.back.update()

		self.linewidth = 1

		self.canvas = ResizingCanvas(back, highlightthickness=0)
		self.canvas.place(relx=rel[2], rely=rel[3], relwidth=rel[0], relheight=rel[1])
		self.canvas.config(bg=Gui.mainColor)
		self.canvas.update()

		width_canvas = rel[0] * self.back.winfo_width()
		height_canvas = rel[1] * self.back.winfo_height()
		size = min(width_canvas, height_canvas)

		# the knob is at the center of the canvas, of radius 2/6 * size
		center = [width_canvas/2, height_canvas/2]
		coord = [center[0] - (size * 2/6)-1, 5, center[0] + (size * 2/6) + 1, size * 4/6 + 7]

		# creates an arc representing the range of the knob, and a line representing tje selected value
		self.coord_arc = coord
		self.r = (coord[2] - coord[0]) / 2  # radius of the arc
		self.center = (coord[0] + coord[2]) / 2, (coord[1] + coord[3]) / 2
		self.arc = self.canvas.create_arc(coord, start=self.arc_start, extent=self.arc_extent,
		                                  fill="", style='arc', width=2)
		self.coord_line = 2 * self.center
		self.line = self.canvas.create_line(self.coord_line, width=self.linewidth, capstyle='round')

		self.font1Ratio = 8 / width_canvas
		self.font2Ratio = 7 / width_canvas
		self.font1size = self.font2size = 0
		self.calcFontSize()

		# cprint("distance = ", int(self.font1size * 5/8))
		self.titleLabel = self.canvas.create_text(self.center[0], coord[3]+int(self.font1size * 5/8), text=title)
		self.canvas.itemconfig(self.titleLabel, font=("Purisa", self.font1size))
		self.label = self.canvas.create_text(self.center[0], coord[3]+int(17/8 * self.font1size), text=0)
		self.canvas.itemconfig(self.label, font=("Purisa", self.font2size))
		# self.canvas.itemconfig(self.label, background="light sky blue")

		self.computeAlphaFromAlphadeg()
		self.redraw_line()
		self.cursorOn = False
		self.cursorOnTitle = False
		self.cx = self.cy = 0

		self.setBinds()

		coords = DrawUtils.computeCoordsCircle(self.r * 1.5, self.center)

		self.oval = self.canvas.create_oval(coords)

		self.canvas.addtag_all("all")

	def updateSizeValues(self):
		# updates self.r and self.center values
		self.canvas.update()
		coord = self.canvas.coords(self.arc)

		self.center = (coord[0] + coord[2]) / 2, (coord[1] + coord[3]) / 2
		self.r = (coord[2] - coord[0]) / 2

		# update labels font size
		self.calcFontSize()
		self.canvas.itemconfig(self.titleLabel, font=("Purisa", self.font1size))
		self.canvas.itemconfig(self.label, font=("Purisa", self.font2size))

	def calcFontSize(self):
		w = self.canvas.winfo_width()

		font1size = int(self.font1Ratio * w)
		font2size = int(self.font2Ratio * w)

		if font1size == font2size:
			font2size -= 1
		self.font1size = (font1size > 0) * font1size + 1 * (font1size <= 0)
		self.font2size = (font2size > 0) * font2size + 1 * (font2size <= 0)

	def valueToSend(self):
		self.dictToSend['value'] = self.valuesTableSend[int(self.value)]
		return self.dictToSend

	def redraw_line(self):
		lx = self.r * np.cos(self.alpha) + self.center[0]
		ly = self.r * np.sin(-self.alpha) + self.center[1]
		self.coord_line = lx, ly, self.center[0], self.center[1]

		self.canvas.coords(self.line, self.coord_line)

	def cursor_on_rotary(self):
		# tests if the cursor is on the rotary knob
		if np.sqrt(np.power(self.cx - self.center[0], 2) + np.power(self.cy - self.center[1], 2)) < self.r:
			self.cursorOn = True
		else:
			self.cursorOn = False
		# tests if it is on the title
		coordsLabel = self.canvas.coords(self.label)
		if (np.abs(self.cx - self.center[0]) < self.r) and \
			(0 < (self.cy - self.coord_arc[3]) < (coordsLabel[1] + self.font2size/2 - self.coord_arc[3])):
			self.cursorOnTitle = True
			# print("On Title")
		else:
			self.cursorOnTitle = False

	def setValue(self, value, sendMidiEvent=False):
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
		alpha = np.arctan2(-self.cy + self.center[1], self.cx - self.center[0])
		alpha_deg = int(alpha * 180 / np.pi)
		alpha_deg = 360 - np.mod(alpha_deg - (self.arc_extent+self.arc_start), 360)

		if alpha_deg > (180+self.arc_extent/2):
			alpha_deg = 0
		elif alpha_deg >= self.arc_extent:
			alpha_deg = self.arc_extent

		# discrete rotation adapted to max value :
		value = np.round(alpha_deg * self.valueMax / 280.)
		alpha_deg = np.round(value*280 / self.valueMax)

		self.alpha_deg = alpha_deg
		self.computeAlphaFromAlphadeg()

	def updateValue(self):

		self.value = np.round(self.value * self.valueMax / 280.)
		self.canvas.itemconfigure(self.label, text=self.valuesTablePrompt[int(self.value)])
		State.events.put(State.Event(self.param, self.valueToSend()))

	def bindMotion(self, posn):
		self.cx = posn.x
		self.cy = posn.y

		if self.cursorOn:
			self.canvas.itemconfigure(self.label, fill='red')
			self.canvas.focus_set()
			self.computeAlphaFromCursor()
			self.redraw_line()
			self.value = self.alpha_deg
			self.updateValue()

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
			self.canvas.itemconfigure(self.label, fill='red')
			self.canvas.focus_set()
			if pressed:
				self.computeAlphaFromCursor()
				self.redraw_line()
				self.value = self.alpha_deg

				self.updateValue()
		else:
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

			self.updateValue()

	def bindUp(self, _):
		self.bindArrowKey(1)

	def bindDown(self, _):
		self.bindArrowKey(-1)

	def setBinds(self):
		self.canvas.bind("<B1-Motion>", self.bindMotion)
		self.canvas.bind("<1>", self.bindPressed)
		self.canvas.bind("<Up>", self.bindUp)
		self.canvas.bind("<Right>", self.bindUp)
		self.canvas.bind("<Down>", self.bindDown)
		self.canvas.bind("<Left>", self.bindDown)
		self.canvas.bind("<ButtonRelease-1>", self.bindReleased)

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


# test the rotary class
if __name__ == "__main__":
	def quit_root(_):
		global rootOn
		rootOn = False
		root.quit()

	root = tk.Tk()
	rootOn = True
	root.title('Rotary Knob')
	root.geometry("300x300")
	back = tk.Frame(master=root)

	back.pack_propagate(0)
	back.pack(fill=tk.BOTH, expand=1)
	root.update()

	back.bind("<KeyPress-q>", quit_root)

	root.update()

	root.resizable(1, 1)

	rel = [0.4, 0.4, 0.1, 0.1]
	r1 = Rotary(back, rel, 0, 'test')

	def setfocus(_):
		back.focus()

	def on_resize(_):
		r1.updateSizeValues()


	back.focus_set()
	back.bind("<1>", setfocus)
	back.bind("<Configure>", on_resize)

	root.aspect(300, 300, 300, 300)

	while rootOn:
		try:
			State.events.get(block=False)
		except queue.Empty:
			pass
		root.update_idletasks()
		root.update()
