import tkinter as tk
from abc import ABC

from AudioLib.Utils import notesList
from Gui.Rotary import Rotary
# from Dev.DebugUtils import *
from Gui.ResizingCanvas import ResizingCanvas
from Gui import Buttons
from Gui import WaveSelect
from Gui import Gui


class Section(ABC):
	def __init__(self, gui):
		super().__init__()
		self.name = ""
		self.rots = []
		self.titles = []
		self.buttons = []
		self.wavebuttons = []
		self.sectionTitles = []

		self.mainBack = gui.back
		self.gui = gui
		self.back = None

		self.relHeight = 0
		self.currentID = 0
		self.currentButtonID = 0

		self.rotWidth = 0

		self.sectionTitles = []
		self.relHeight = 0

	def drawSection(self):
		pass

	def drawGrid(self, relw, relh, gridX, gridY, **kwargs):
		try:
			back = kwargs['back']
		except KeyError:
			back = self.back
		if not isinstance(back, tk.Frame):
			back = self.back

		# center the canvas if its width is < available width
		x_offset = (1/gridX - relw) / 2

		for i in range(gridY):
			rely = self.relHeight
			self.relHeight += relh
			for j in range(gridX):
				relx = j/gridX + x_offset
				rel = [relw, relh, relx, rely]
				rot = Rotary(back, rel, self.currentID)
				rot.dictToSend['rottype'] = self.name
				rot.dictToSend['rotid'] = self.currentID

				self.rots.append(rot)

				self.setTitle(self.currentID)
				self.currentID += 1

	def setTitle(self, ID):
		try:
			title = self.titles[ID]
		except IndexError:
			title = 'Undef'
		self.rots[-1].setTitle(title)
		if self.rots[-1].param == "":
			self.rots[-1].param = title

	def addTagAll(self):
		for r in self.rots:
			r.canvas.addtag_all("all")
		for b in self.buttons:
			b.canvas.addtag_all("all")

	def createSectionTitle(self, title, **kwargs):
		try:
			back = kwargs['back']
		except KeyError:
			back = self.back
		try:
			scale = kwargs['scale']
		except KeyError:
			scale = 1
		back.update()
		sectionW = back.winfo_width()
		sectionH = back.winfo_height()
		relHeight = 20 / sectionH

		titleCanvas = ResizingCanvas(back, highlightthickness=0, bg=Gui.mainColor)
		titleCanvas.place(relx=(1 - scale)/2, rely=self.relHeight, relwidth=scale, relheight=relHeight)

		titleCanvas.update()

		self.relHeight += relHeight
		titleX = titleCanvas.winfo_width()/2
		titleY = titleCanvas.winfo_height()/2
		titleID = titleCanvas.create_text(titleX, titleY, text=title)
		titleCanvas.itemconfig(titleID, font=("Purisa", 8))
		titleCanvas.coords(titleID, (sectionW / 2, 10))
		bbox = titleCanvas.bbox(titleID)

		bbox = [bbox[0] - 1, bbox[1] - 1, bbox[2], bbox[3]]

		titleCanvas.create_line(0, 10, bbox[0] - 3, 10)
		titleCanvas.create_line(bbox[2] + 3, 10, sectionW, 10)

		titleCanvas.create_rectangle(bbox, fill='black')
		titleCanvas.itemconfig(titleID, fill='white')
		titleCanvas.tag_raise(titleID)

		titleCanvas.addtag_all("all")

		self.sectionTitles.append((titleCanvas, titleID))

	def drawButtons(self, **kwargs):
		try:
			back = kwargs['back']
		except KeyError:
			back = self.back
		if not isinstance(back, tk.Frame):
			back = self.back
		rows = kwargs['rows']
		columns = kwargs['columns']
		width = kwargs['width']
		canvasH = kwargs['canvasH']

		relw = 1/columns
		sectionW = back.winfo_width()
		sectionH = back.winfo_height()
		canvasW = relw * sectionW
		relh = canvasH / sectionH
		buttonRel = [width/canvasW, 20/canvasH]

		for j in range(rows):
			rely = self.relHeight
			for i in range(columns):
				relx = i/columns
				rel = [relx, rely, relw, relh]

				seqID = j+1
				clkID = i+1

				self.addButton(back, rel, buttonRel, seqID=seqID, clkID=clkID)

				self.currentButtonID += 1

			self.relHeight += relh

	def addButton(self, *_, **_1):
		pass

	def resize(self):
		for r in self.rots:
			r.updateSizeValues()
		font1size = self.rots[0].font1size
		for (canvas, ID) in self.sectionTitles:
			canvas.itemconfig(ID, font=("Purisa", font1size))
		for button in self.buttons:
			button.button.config(font=("Purisa", font1size))
		for wavebutton in self.wavebuttons:
			wavebutton.updateSizeValues()


class RhythmSection(Section):
	def __init__(self, gui):
		super().__init__(gui)
		self.name = "rhythm"
		self.titles = ["Step1Seq1", "Step2Seq1", "Step3Seq1", "Step4Seq1"]
		self.titles.extend(["Step1Seq2", "Step2Seq2", "Step3Seq2", "Step4Seq2"])
		self.titles.extend(["Clk1", "Clk2", "Clk3", "Clk4"])

		self.back = tk.Frame(master=self.mainBack)
		self.configureBack()

		self.sectionH = self.back.winfo_height()
		self.sectionW = self.back.winfo_width()

		self.drawSection()

	def configureBack(self):
		self.back.bind(self.back.bind("<KeyPress-q>", self.gui.quit_root))
		relh = 346 / self.mainBack.winfo_height()
		relw = 240 / self.mainBack.winfo_width()
		relx = 22 / self.mainBack.winfo_height()
		rely = 17 / self.mainBack.winfo_width()
		self.back.place(relx=relx, rely=rely, relheight=relh, relwidth=relw)
		self.back.config(bg=Gui.mainColor)
		self.back.update()

	def drawSection(self):

		# calc size of the rots
		relh = 80 / self.sectionH
		relw = 60 / self.sectionW

		# draw all the elements
		self.createSectionTitle("Sequencer 1")
		self.drawGrid(relw, relh, 4, 1)
		self.createSectionTitle("Sequencer 2")
		self.drawGrid(relw, relh, 4, 1)
		self.createSectionTitle("Rhythm")
		self.drawGrid(relw, relh, 4, 1)
		self.drawButtons(width=45, rows=2, columns=4, canvasH=23)

	def setTitle(self, ID):
		try:
			title = self.titles[ID]
		except IndexError:
			title = 'Undef'
		if title[:4] == "Step":
			self.rots[ID].valueMax = 15
			self.rots[ID].param = 'Step' + title[4] + title[8]

			self.rots[ID].valuesTablePrompt = [17 - i for i in range(1, 17)]
			self.rots[ID].valuesTableSend = self.rots[ID].valuesTablePrompt

			self.rots[ID].dictToSend['messagetype'] = 'step'
			self.rots[ID].dictToSend['stepid'] = int(title[4])
			self.rots[ID].dictToSend['seqid'] = int(title[8])

			self.rots[ID].canvas.itemconfig(self.rots[ID].arc, outline='DeepSkyBlue2')

			title = title[:5]
		elif title[:3] == 'Clk':
			self.rots[ID].valueMax = 15
			self.rots[ID].valuesTablePrompt = [17 - i for i in range(1, 17)]
			self.rots[ID].valuesTableSend = self.rots[ID].valuesTablePrompt

			self.rots[ID].dictToSend['clkid'] = int(title[3])
			self.rots[ID].dictToSend['messagetype'] = 'clk'
			self.rots[ID].canvas.itemconfig(self.rots[ID].arc, outline='red')

		self.rots[ID].setValue(1)
		self.rots[ID].setTitle(title)
		if self.rots[ID].param == "":  # only used by Clk rots
			self.rots[ID].param = title

	def addButton(self, back, rel, buttonRel, **kwargs):
		seqID = kwargs['seqID']
		clkID = kwargs['clkID']
		self.buttons.append(Buttons.RythmButton(back, rel, buttonRel, seqID, clkID))


class VcoSection(Section):
	def __init__(self, gui):
		super().__init__(gui)
		self.name = "vco"
		self.titles = ['Vco1', 'Sub12', 'Sub23', 'Vco1 level0', 'Sub1 level2', 'Sub2 level3']
		self.titles.extend(['Vco2', 'Sub14', 'Sub25', 'Vco2 level1', 'Sub1 level4', 'Sub2 level5'])

		self.buttonTitles = ['osc1', 'sub1', 'sub2', 'osc2', 'sub1', 'sub2']
		self.voicesID = [0, 2, 3, 1, 4, 5]
		# self.voicesID = [0, 1, 2, 3, 4, 5]

		self.back = tk.Frame(master=self.mainBack)
		self.configureBack()

		self.sectionH = self.back.winfo_height()
		self.sectionW = self.back.winfo_width()

		self.drawSection()

	def configureBack(self):
		self.back.bind(self.back.bind("<KeyPress-q>", self.gui.quit_root))
		relh = (395 - 17) / self.mainBack.winfo_height()
		relw = (580 - 286) / self.mainBack.winfo_width()
		relx = 286 / self.mainBack.winfo_width()  # + 0.1
		rely = 17 / self.mainBack.winfo_height()
		self.back.place(relx=relx, rely=rely, relheight=relh, relwidth=relw)
		self.back.config(bg="white")
		self.back.update()

	def drawSection(self):
		# calc size of the rots
		relh = 75 / self.sectionH
		relw = 2 * 60 / self.sectionW
		mainRelh = 80 / self.sectionH
		mainRelw = 1
		for i in range(2):
			self.relHeight = 0
			# create and configure back for one vco
			vcoback = tk.Frame(master=self.back)
			vcoback.bind("<KeyPress-q>", self.gui.quit_root)
			vcoback.place(relx=i/2, rely=0, relheight=1, relwidth=1/2)
			vcoback.config(bg=Gui.mainColor)
			vcoback.update()

			# draw the vcoX subsection
			self.createSectionTitle("Vco " + str(i+1), back=vcoback)
			self.drawGrid(mainRelw, mainRelh, 1, 1, back=vcoback)

			# move up the label, otherwise it is outside of the canvas when resizing
			x, y = self.rots[-1].canvas.coords(self.rots[-1].label)
			self.rots[-1].canvas.coords(self.rots[-1].label, (x, y-2))

			self.drawGrid(relw, relh, 2, 1, back=vcoback)
			self.createSectionTitle("Seq" + str(i + 1) + "Assign", back=vcoback, scale=0.95)
			self.drawButtons(back=vcoback, width=39, rows=1, columns=3, canvasH=30)
			self.drawGrid(mainRelw, mainRelh, 1, 1, back=vcoback)
			x, y = self.rots[-1].canvas.coords(self.rots[-1].label)
			self.rots[-1].canvas.coords(self.rots[-1].label, (x, y - 2))
			# self.relHeight -= 10 / self.sectionH
			self.drawGrid(relw, relh, 2, 1, back=vcoback)

			self.addWaveSelect(vcoback, i)

		# draw a line btw the two vco sections
		lineCanvas = ResizingCanvas(self.back, highlightthickness=0, bg='black')
		lineCanvas.place(relx=0.5, rely=0, width=1, relheight=1)
		lineCanvas.update()

		self.rots[0].canvas.tag_raise(self.rots[0].label)
		self.rots[0].canvas.tag_raise(self.rots[0].titleLabel)
		self.rots[0].canvas.lift(self.rots[0].label)
		self.rots[0].canvas.lift(self.rots[0].titleLabel)

	def addWaveSelect(self, back, i):
		waveSelectW = 8
		back.update()
		relh = (3 * waveSelectW + 5) / back.winfo_height()
		relw = (2 * waveSelectW + 1) / back.winfo_width()
		relx = relw/2 + i * (1 - 2 * relw)
		rely = 0.1

		waveCanvas = ResizingCanvas(back, highlightthickness=0, bg=Gui.mainColor)
		waveCanvas.place(relx=relx, rely=rely, relwidth=relw, relheight=relh)

		waveCanvas.update()
		self.wavebuttons.append(WaveSelect.WaveSelect(waveCanvas, waveSelectW, [waveSelectW * (i == 0), 0], 1 - 2 * i, i))

	def setTitle(self, ID):
		try:
			title = self.titles[ID]
		except IndexError:
			title = 'Undef'
		idsVco1 = [i for i in range(6)]

		if title[:3] == "Sub" and len(title) == 5:
			self.rots[ID].param = title
			self.rots[ID].valueMax = 15
			self.rots[ID].valuesTablePrompt = [17 - i for i in range(1, 17)]
			self.rots[ID].valuesTableSend = self.rots[ID].valuesTablePrompt
			self.rots[ID].dictToSend['voiceid'] = int(title[4])
			self.rots[ID].dictToSend['messagetype'] = 'sub'
			title = title[:4]
		elif title[:3] == 'Vco' and len(title) == 4:
			self.rots[ID].valuesTablePrompt = notesList()
			self.rots[ID].dictToSend['vcoid'] = int(title[3])
			self.rots[ID].dictToSend['voiceid'] = int(title[3]) - 1
			self.rots[ID].dictToSend['messagetype'] = 'vco'
		elif title[5:10] == 'level':
			self.rots[ID].param = 'level' + title[10]
			self.rots[ID].dictToSend['voiceid'] = int(title[10])
			self.rots[ID].dictToSend['messagetype'] = 'level'
			title = title[:10]

		if ID not in idsVco1:
			self.rots[ID].canvas.itemconfig(self.rots[ID].arc, outline='dark orange')
		else:
			self.rots[ID].canvas.itemconfig(self.rots[ID].arc, outline='SpringGreen2')

		self.rots[ID].setTitle(title)

		if self.rots[ID].param == "":
			self.rots[ID].param = title

	def addButton(self, back, rel, buttonRel, **_):
		self.buttons.append(Buttons.VcoButton(back, rel, buttonRel, self.currentButtonID,
		                                      self.voicesID[self.currentButtonID],
		                                      self.buttonTitles))


class GeneralSection(Section):
	def __init__(self, gui):
		super().__init__(gui)
		self.name = "general"
		self.titles = ["Vol", "Tempo"]

		self.back = tk.Frame(master=self.mainBack)
		self.configureBack()

		self.sectionH = self.back.winfo_height()
		self.sectionW = self.back.winfo_width()

		self.drawSection()

	def configureBack(self):
		self.back.bind(self.back.bind("<KeyPress-q>", self.gui.quit_root))
		relh = 123 / self.mainBack.winfo_height()
		relw = (206 - 22) / self.mainBack.winfo_width()
		relx = 22 / self.mainBack.winfo_width()  # - 0.1
		rely = 406 / self.mainBack.winfo_height()
		self.back.place(relx=relx, rely=rely, relheight=relh, relwidth=relw)
		self.back.config(bg=Gui.mainColor)
		self.back.update()

	def drawSection(self):
		# calc size of the rots
		mainRelh = 87 / self.sectionH
		mainRelw = 1/2

		self.createSectionTitle("General")
		self.relHeight += 0.13
		self.drawGrid(mainRelw, mainRelh, 2, 1)

	def setTitle(self, ID):
		try:
			title = self.titles[ID]
		except IndexError:
			title = 'Undef'

		self.rots[ID].setTitle(title)
		self.rots[ID].canvas.itemconfig(self.rots[ID].arc, outline='DeepSkyBlue3')
		if self.rots[ID].param == "":
			self.rots[ID].param = title


class FilterSection(Section):
	def __init__(self, gui):
		super().__init__(gui)
		self.name = "filter"
		self.titles = ['fc', 'Q', 'EG Amount']
		self.titles.extend(['A filter', 'D filter'])

		self.back = tk.Frame(master=self.mainBack)
		self.configureBack()

		self.sectionH = self.back.winfo_height()
		self.sectionW = self.back.winfo_width()

		self.drawSection()

	def configureBack(self):
		self.back.bind(self.back.bind("<KeyPress-q>", self.gui.quit_root))
		relh = 160 / self.mainBack.winfo_height()
		relw = (579 - 380) / self.mainBack.winfo_width()
		relx = 380 / self.mainBack.winfo_width()  # + 0.1
		rely = 406 / self.mainBack.winfo_height()
		self.back.place(relx=relx, rely=rely, relheight=relh, relwidth=relw)
		self.back.config(bg=Gui.mainColor)
		self.back.update()

	def drawSection(self):
		def createSubframe(w, x):
			cutoffback = tk.Frame(master=self.back)
			cutoffback.bind(self.back.bind("<KeyPress-q>", self.gui.quit_root))
			cutoffback.place(relx=x, rely=self.relHeight, relheight=1, relwidth=w)
			cutoffback.config(bg=Gui.mainColor)
			cutoffback.update()
			return cutoffback

		self.createSectionTitle("Filter")

		cutoffback = createSubframe(0.4, 0)
		mainRelh = 87 / self.sectionH
		self.relHeight = 0.13 * self.sectionH / cutoffback.winfo_height()
		self.drawGrid(1, mainRelh, 1, 1, back=cutoffback)

		self.relHeight = self.sectionTitles[0][0].winfo_height()/self.sectionH

		restBack = createSubframe(0.6, 0.4)

		self.relHeight = 0
		relh = 70 / restBack.winfo_height()
		relw = 1/2
		self.drawGrid(relw, relh, 2, 2, back=restBack)

	def setTitle(self, ID):
		try:
			title = self.titles[ID]
		except IndexError:
			title = 'Undef'

		if title == 'Q':
			self.rots[ID].valueMax = 1000
			self.rots[ID].valuesTablePrompt = [i * 15. / self.rots[ID].valueMax
			                                  for i in range(self.rots[ID].valueMax)]
			# self.r[-1].valuesTablePrompt = np.arange(10)
			self.rots[ID].param = title
			title = 'Reso'
			self.rots[ID].valuesTableSend = self.rots[ID].valuesTablePrompt
		elif title == 'fc':

			# debug : commenting these three lines

			# self.rots[ID].valueMax = 12700
			# self.rots[ID].valuesTablePrompt = [i * 127 / self.rots[ID].valueMax
			# for i in range(self.rots[ID].valueMax)]
			# self.rots[ID].valuesTableSend = self.rots[ID].valuesTablePrompt

			self.rots[ID].param = title
			title = 'Cutoff'

		elif 'filter' in title:
			self.rots[ID].param = title
			title = title[:1]

		self.rots[ID].canvas.itemconfig(self.rots[ID].arc, outline='DarkOrchid1')

		self.rots[ID].setTitle(title)
		if self.rots[ID].param == "":
			self.rots[ID].param = title


class EnvSection(Section):
	def __init__(self, gui):
		super().__init__(gui)
		self.name = "env"
		self.titles = ['A', 'D']
		self.titles.extend(['S', 'R'])

		self.back = tk.Frame(master=self.mainBack)
		self.configureBack()

		self.sectionH = self.back.winfo_height()
		self.sectionW = self.back.winfo_width()

		self.drawSection()

	def configureBack(self):
		self.back.bind(self.back.bind("<KeyPress-q>", self.gui.quit_root))
		relh = 160 / self.mainBack.winfo_height()
		relw = (354 - 235) / self.mainBack.winfo_width()
		relx = 235 / self.mainBack.winfo_width()  # + 0.1
		rely = 406 / self.mainBack.winfo_height()
		self.back.place(relx=relx, rely=rely, relheight=relh, relwidth=relw)
		self.back.config(bg="white")
		self.back.update()

	def drawSection(self):

		self.createSectionTitle("Env")

		relh = 70 / self.sectionH
		relw = 1 / 2
		self.drawGrid(relw, relh, 2, 2)

	def setTitle(self, ID):
		try:
			title = self.titles[ID]
		except IndexError:
			title = 'Undef'

		self.rots[ID].setTitle(title)
		self.rots[ID].canvas.itemconfig(self.rots[ID].arc, outline='SpringGreen3')

		if self.rots[ID].param == "":
			self.rots[ID].param = title
