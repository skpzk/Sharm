import multiprocessing
import tkinter as tk
import queue

from State import State
from Gui import Sections

# import PatchBay  # will be used in a future version

events = multiprocessing.Queue(maxsize=10)

COLORS = True
mainColor = 'white'


class Gui:
	def __init__(self, root):
		self.root = root
		self.configureRoot()

		self.back = tk.Frame(master=self.root)
		self.configureBack()

		self.On = True  # when set to false, close the loops

		self.rhythmSection = Sections.RhythmSection(self)
		self.vcoSection = Sections.VcoSection(self)
		self.generalSection = Sections.GeneralSection(self)
		self.filterSection = Sections.FilterSection(self)
		self.envSection = Sections.EnvSection(self)

		self.sections = [self.rhythmSection,
		                 self.vcoSection,
		                 self.generalSection,
		                 self.filterSection,
		                 self.envSection]

		self.setBinds()

		self.back.focus_set()

		self.rhythmSection.addTagAll()
		self.vcoSection.addTagAll()

	def configureRoot(self):
		self.root.title('Sharm')
		# self.root.geometry("900x600+0+0")  # geometry when Patchbay is used
		w = 605
		h = 600
		geom = str(w) + 'x' + str(h) + '+500+10'
		self.root.geometry(geom)  # geometry when Patchbay is not used

		# get screen size to allow resizing
		screenW = self.root.winfo_screenwidth()
		screenH = self.root.winfo_screenheight()

		ratio = min(screenW / w, screenH / h)

		self.root.aspect(w, h, w, h)  # force fixed aspect ratio
		self.root.minsize(int(w / 2), int(h / 2))  # force minimum size
		self.root.maxsize(int(ratio * w), int(ratio * h))  # force maximum size and prevents maximizing

	def configureBack(self):
		self.back.pack_propagate(0)
		self.back.pack(fill=tk.BOTH, expand=1)
		self.back.config(bg=mainColor)
		# self.back.config(bg='light sky blue')
		self.root.update()

	def setBinds(self):
		self.back.bind("<KeyPress-q>", self.quit_root)
		self.back.bind("<Destroy>", self.quit_root)
		self.back.bind("<1>", self.setfocus)
		self.back.bind("<Configure>", self.on_resize)

	def quit_root(self, _event=""):
		self.root.quit()
		self.On = False
		State.events.put(State.Event(-1, -1))
		print("Stop signal send from gui")

	def createMenuBar(self):
		menubar = tk.Menu(self.root, relief=tk.FLAT, bg='white', activebackground='white')

		filemenu = tk.Menu(menubar, tearoff=0, bg='white', activebackground='white')
		filemenu.add_command(label="New", command=self.donothing)
		filemenu.add_command(label="Open", command=self.donothing)
		filemenu.add_command(label="Save", command=self.donothing)
		filemenu.add_command(label="Save as...", command=self.donothing)
		filemenu.add_command(label="Close", command=self.donothing)

		filemenu.add_separator()

		filemenu.add_command(label="Exit", command=self.quit_root)
		menubar.add_cascade(label="File", menu=filemenu)
		editmenu = tk.Menu(menubar, tearoff=0, bg='white', activebackground='white')
		editmenu.add_command(label="Undo", command=self.donothing)

		editmenu.add_separator()

		editmenu.add_command(label="Cut", command=self.donothing)
		editmenu.add_command(label="Copy", command=self.donothing)
		editmenu.add_command(label="Paste", command=self.donothing)
		editmenu.add_command(label="Delete", command=self.donothing)
		editmenu.add_command(label="Select All", command=self.donothing)

		menubar.add_cascade(label="Edit", menu=editmenu)
		helpmenu = tk.Menu(menubar, tearoff=0, bg='white', activebackground='white')
		helpmenu.add_command(label="Help Index", command=self.donothing)
		helpmenu.add_command(label="About...", command=self.donothing)
		menubar.add_cascade(label="Help", menu=helpmenu)

		self.root.config(menu=menubar)

	def donothing(self):
		filewin = tk.Toplevel(self.root)
		button = tk.Button(filewin, text="Do nothing button", command=filewin.destroy, highlightthickness=0)
		button.bind("<Return>", lambda event: filewin.destroy())
		button.focus_set()
		button.pack()

	def setfocus(self, _):
		self.back.focus()

	def on_resize(self, _):
		for section in self.sections:
			section.resize()

	def noteOn(self, ID, step):
		for r in self.rhythmSection.rots:
			try:
				seqN = r.dictToSend['seqid']
				if seqN == ID:
					if r.dictToSend['stepid'] == step + 1:
						r.noteOn()
			except KeyError:
				pass

	def noteOff(self, ID, step):
		for r in self.rhythmSection.rots:
			try:
				seqN = r.dictToSend['seqid']
				if seqN == ID:
					if r.dictToSend['stepid'] == step + 1:
						r.noteOff()
			except KeyError:
				pass

	def checkQueue(self):
		try:
			message = events.get(block=False)
			if isinstance(message, State.Event):
				self.change(message)
		except queue.Empty:
			pass

	def checkQueueLoop(self):
		while self.On:
			# print("On")
			self.checkQueue()

	def change(self, message):
		if message.value['type'] == 'seqnote':
			if message.param == 'note on':
				seqid = message.value['seqid']
				step = message.value['step']
				self.noteOn(seqid, step)
			elif message.param == 'note off':
				seqid = message.value['seqid']
				step = message.value['step']
				self.noteOff(seqid, step)
		elif message.param == 'quit':
			self.quit_root()
		else:
			self.applyToGui(message.value)

	def applyToGui(self, valuesDict):
		if 'value' in valuesDict.keys():
			value = valuesDict['value']
		else:
			value = None
		if valuesDict['type'] != 'rot':
			self.applyToGuiButton(valuesDict)
		else:
			self.applyToGuiRot(valuesDict, value)

	def applyToGuiButton(self, valuesDict):
		# print(valuesDict)
		if valuesDict['buttontype'] == 'rhythm':
			ID = int(valuesDict['buttonid'])
			state = int(valuesDict['state'])
			self.rhythmSection.buttons[ID].toggle(state=state, sendEvent=False)

		elif valuesDict['buttontype'] == 'vco':
			ID = int(valuesDict['id'])
			state = int(valuesDict['state'])
			self.vcoSection.buttons[ID].toggle(state=state, sendEvent=False)

		elif valuesDict['buttontype'] == 'wave':
			ID = int(valuesDict['id'])
			wave = valuesDict['wave']
			self.vcoSection.wavebuttons[ID].toggle(wave)

	def applyToGuiRot(self, valuesDict, value):
		ID = valuesDict['rotid']
		if valuesDict['rottype'] == 'general':
			self.generalSection.rots[ID].setValue(value)

		elif valuesDict['rottype'] == 'rhythm':
			self.rhythmSection.rots[ID].setValue(value)

		elif valuesDict['rottype'] == 'vco':
			self.vcoSection.rots[ID].setValue(value)

		elif valuesDict['rottype'] == 'env':
			self.envSection.rots[ID].setValue(value)

		elif valuesDict['rottype'] == 'filter':
			self.filterSection.rots[ID].setValue(value)
