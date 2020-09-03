# import tkinter as tk
# import numpy as np
import queue

from functools import partial
import multiprocessing

from State.State import Event
# from Gui import DrawUtils
from Gui.Selectors import *

from State import State
from AudioLib.Utils import *

# import PatchBay  # will be used in a future version

events = multiprocessing.Queue(maxsize=10)

COLORS = True


class Gui:
	def __init__(self, root):
		self.root = root
		self.root.title('Sharm')
		# self.root.geometry("900x600+0+0")  # geometry when Patchbay is used
		self.root.geometry("640x600+0+0")  # geometry when Patchbay is not used
		self.back = tk.Frame(master=self.root)
		self.back.pack_propagate(0)
		self.back.pack(fill=tk.BOTH, expand=1)
		self.back.config(bg='white')

		self.back.bind("<KeyPress-q>", self.quit_root)
		# self.back.bind("<FocusOut>", self.quit_root)
		self.back.bind("<Destroy>", self.quit_root)
		# self.back.bind('<Motion>', self.updatePos)

		self.On = True

		self.width = 50
		self.border = 10

		self.root.update()  # Otherwise the winfo method only returns '1'
		# print(root.winfo_width())

		self.createMenuBar()

		self.offset_y = self.root.winfo_height() - self.width - self.border - 20
		self.offset_x = int(self.root.winfo_width() / 6) - self.width - self.border

		self.dimGrid = [4, 6]
		self.nbRot = self.dimGrid[0] * self.dimGrid[1]
		self.r = []

		self.titleRythmRots = ["Step1Seq1", "Step2Seq1", "Step3Seq1", "Step4Seq1"]
		self.titleRythmRots.extend(["Step1Seq2", "Step2Seq2", "Step3Seq2", "Step4Seq2"])
		self.titleRythmRots.extend(["Clk1", "Clk2", "Clk3", "Clk4"])
		self.seqMode = 'sub'

		self.titleOtherRot = ["Vol", "Tempo"]

		self.rythmButtons = []
		self.rythmRots = []

		self.vcoRots = []
		self.vcoButtons = []

		self.filterRots = []
		self.envRots = []

		self.createRythmSection()
		self.createVcoSection()
		self.createOtherRots()

		self.createFilterSection()
		self.createEnvSection()

		self.back.focus_set()
		self.back.bind("<1>", self.setfocus)

		# self.patchBay = PatchBay.PatchBay(root, self.back)

	def quit_root(self, _event=""):
		# self.running = False
		self.root.quit()
		self.On = False
		State.events.put(Event(-1, -1))
		print("Stop signal send from gui")

	def setfocus(self, _):
		# print("Focus on back")
		self.back.focus()

	def createRythmSection(self):
		gridX = 4
		gridY = 3

		offset_x = 22
		offset_y = 40

		width = 40

		distanceX = 60
		distanceY = 100
		for i in range(gridY):
			for j in range(gridX):

				pos = (offset_x + j * distanceX, offset_y + i * distanceY)
				ID = i * gridX + j
				self.rythmRots.append(Rotary(self.back, width, pos, ID, self))
				self.rythmRots[-1].dictToSend['rottype'] = 'rythmrot'
				self.rythmRots[-1].dictToSend['rotid'] = ID
				try:
					title = self.titleRythmRots[ID]
				except IndexError:
					title = 'Undef'
				if title[:4] == "Step":
					self.rythmRots[-1].valueMax = 15
					self.rythmRots[-1].param = 'Step' + title[4] + title[8]

					self.rythmRots[-1].valuesTablePrompt = [17 - i for i in range(1, 17)]
					self.rythmRots[-1].valuesTableSend = self.rythmRots[-1].valuesTablePrompt

					self.rythmRots[-1].dictToSend['messagetype'] = 'step'
					self.rythmRots[-1].dictToSend['stepid'] = int(title[4])
					self.rythmRots[-1].dictToSend['seqid'] = int(title[8])

					if COLORS:
						self.rythmRots[-1].canvas.itemconfig(self.rythmRots[-1].arc, outline='DeepSkyBlue2')

					title = title[:5]
				elif title[:3] == 'Clk':
					self.rythmRots[-1].valueMax = 15
					self.rythmRots[-1].valuesTablePrompt = [17 - i for i in range(1, 17)]
					self.rythmRots[-1].valuesTableSend = self.rythmRots[-1].valuesTablePrompt

					self.rythmRots[-1].dictToSend['clkid'] = int(title[3])
					self.rythmRots[-1].dictToSend['messagetype'] = 'clk'
					if COLORS:
						self.rythmRots[-1].canvas.itemconfig(self.rythmRots[-1].arc, outline='red')

				self.rythmRots[-1].setTitle(title)
				if self.rythmRots[-1].param == "":  # only used by Clk rots
					self.rythmRots[-1].param = title
		for i in range(4):
			for j in range(2):
				width = 45
				height = 20

				# position = [offset_x + i * distanceX, distanceY * gridY + j * (height + 3) + 12]
				position = [self.rythmRots[i].centerAbs[0] - width/2,
				            self.rythmRots[-1].centerAbs[1] + distanceY/2 + j * (height + 3) + 8]

				seqID = j+1

				self.rythmButtons.append(RythmButton(self.back, width, height, position, seqID, i+1))
				self.rythmButtons[-1].button.config(command=partial(self.rythmButtonAction, i * 2 + j))

		# DrawUtils.drawCross(tk.Canvas(self.back, width=800, height=600), pos)

		over = 5

		self.createRhythmTitleSection(width + 2*over, offset_x-over, offset_y, 'Sequencer 1')
		self.createRhythmTitleSection(width + 2*over, offset_x-over, offset_y + distanceY, 'Sequencer 2')
		self.createRhythmTitleSection(width + 2*over, offset_x-over, offset_y + 2*distanceY, 'Rhythm')

	def createRhythmTitleSection(self, width, offset_x, offset_y, title):
		sectionWidth = (self.rythmRots[-1].centerAbs[0] + width / 2) - (self.rythmRots[0].centerAbs[0] - width / 2)
		titleheight = 20
		titleX = (self.rythmRots[0].centerAbs[0] - width / 2)
		titleY = offset_y - titleheight - 5

		titleCanvas = tk.Canvas(self.back, width=sectionWidth, height=titleheight, highlightthickness=0, bg='white')
		titleCanvas.place(x=titleX, y=titleY)
		titleID = titleCanvas.create_text(0, 0, text=title)
		titleCanvas.itemconfig(titleID, font=("Purisa", 8))
		titleCanvas.coords(titleID, (sectionWidth / 2, 10))
		bbox = titleCanvas.bbox(titleID)

		# print(bbox)
		bbox = [bbox[0] - 1, bbox[1] - 1, bbox[2], bbox[3]]

		titleCanvas.create_line(0, 10, bbox[0] - 3, 10)
		titleCanvas.create_line(bbox[2] + 3, 10, sectionWidth, 10)

		titleCanvas.create_rectangle(bbox, fill='black')
		titleCanvas.itemconfig(titleID, fill='white')
		titleCanvas.tag_raise(titleID)

	def createVcoRot(self, widthMain, pos, ID, titles):
		self.vcoRots.append(Rotary(self.back, widthMain, pos, ID, self))
		self.vcoRots[-1].dictToSend['rottype'] = 'vcorot'
		self.vcoRots[-1].dictToSend['rotid'] = ID
		title = titles[ID]
		idsVco1 = [0, 2, 3, 6, 8, 9]

		if title[:3] == "Sub" and len(title) == 5:
			self.vcoRots[-1].param = title
			self.vcoRots[-1].valueMax = 15
			self.vcoRots[-1].valuesTablePrompt = [17 - i for i in range(1, 17)]
			self.vcoRots[-1].valuesTableSend = self.rythmRots[-1].valuesTablePrompt
			self.vcoRots[-1].dictToSend['voiceid'] = int(title[4])
			self.vcoRots[-1].dictToSend['messagetype'] = 'sub'
			title = title[:4]
		elif title[:3] == 'Vco' and len(title) == 4:
			self.vcoRots[-1].valuesTablePrompt = notesList()
			self.vcoRots[-1].dictToSend['vcoid'] = int(title[3])
			self.vcoRots[-1].dictToSend['voiceid'] = int(title[3])
			self.vcoRots[-1].dictToSend['messagetype'] = 'vco'
		elif title[5:10] == 'level':
			self.vcoRots[-1].param = 'level' + title[10]
			self.vcoRots[-1].dictToSend['id'] = int(title[10])
			self.vcoRots[-1].dictToSend['messagetype'] = 'level'
			title = title[:10]

		if COLORS:
			if ID not in idsVco1:
				self.vcoRots[-1].canvas.itemconfig(self.rythmRots[-1].arc, outline='dark orange')
			else:
				self.vcoRots[-1].canvas.itemconfig(self.rythmRots[-1].arc, outline='SpringGreen2')

		self.vcoRots[-1].setTitle(title)

		if self.vcoRots[-1].param == "":
			self.vcoRots[-1].param = title

	def createVcoSection(self):
		gridX = 4
		gridY = 3

		offset_x = 280
		offset_y = 40

		width = 40
		widthMain = 56

		distanceX = 68
		distanceY = 75
		distanceYMain = 80

		mainSpaceX = 10

		titles = ['Vco1', 'Vco2', 'Sub12', 'Sub23', 'Sub24', 'Sub25', 'Vco1 level0', 'Vco2 level1']
		titles.extend(['Sub1 level2', 'Sub2 level3', 'Sub1 level4', 'Sub2 level5'])

		x0 = offset_x + (2 * distanceX - widthMain) / 2
		y0 = offset_y
		pos = (x0, y0)

		ID = 0
		self.createVcoRot(widthMain, pos, ID, titles)

		pos = (x0 + 2 * distanceX + mainSpaceX, y0)
		ID = 1
		self.createVcoRot(widthMain, pos, ID, titles)

		off = 0
		for i in range(2, 6):
			ID = i
			if i > 3:
				off = 1
			pos = (offset_x + (i-2) * distanceX + (distanceX - width) / 2 + off * mainSpaceX, y0 + distanceYMain)
			self.createVcoRot(width, pos, ID, titles)

		buttonSpaceX = 5
		buttonWidth = (2 * distanceX - 4 * buttonSpaceX)/3
		buttonHeight = 20
		buttonDistanceX = buttonSpaceX + buttonWidth
		buttonDistanceY = 50
		buttonCanvasWidth = 6 * buttonWidth + 8 * buttonSpaceX + mainSpaceX

		vcoSectionWidth = 4*distanceX + mainSpaceX

		canvasX = np.mean([self.vcoRots[0].centerAbs[0], self.vcoRots[1].centerAbs[0]]) - buttonCanvasWidth/2
		canvasY = y0 + distanceYMain + distanceY + 20

		canvas = tk.Canvas(self.back, width=buttonCanvasWidth, height=buttonHeight, highlightthickness=0)
		canvas.place(x=canvasX, y=canvasY, width=buttonCanvasWidth, height=buttonHeight)

		canvas.config(bg='white')

		buttonTitles = ['osc1', 'sub1', 'sub2', 'osc2', 'sub1', 'sub2']
		IDs = [0, 2, 3, 1, 4, 5]
		off = 0
		for i in range(6):
			if i == 3:
				off = 1
			position = (buttonSpaceX + i * buttonDistanceX + off * (buttonSpaceX + mainSpaceX), 0)
			ID = i
			voiceID = IDs[i]
			self.vcoButtons.append(VcoButton(canvas, buttonWidth, buttonHeight, position, ID, voiceID, buttonTitles))
			self.vcoButtons[-1].button.config(command=partial(self.vcoButtonAction, ID))

		for i in range(6, 8):
			ID = i
			pos = (x0 + 2 * (i-6) * distanceX + (i == 7)*mainSpaceX, y0 + distanceY + distanceYMain + buttonDistanceY)
			self.createVcoRot(widthMain, pos, ID, titles)

		for i in range(8, 12):
			ID = i
			pos = (offset_x + (i-8) * distanceX + (distanceX - width) / 2 + (i > 9)*mainSpaceX, y0 + distanceY + 2 * distanceYMain + buttonDistanceY)
			self.createVcoRot(width, pos, ID, titles)

		# create the titles for the vco section
		self.createVcoTitleSection(2 * distanceX + mainSpaceX, 0, offset_y, "1")
		self.createVcoTitleSection(2 * distanceX + mainSpaceX, 1, offset_y, "2")
		self.createVcoTitleSection(2 * distanceX - 5, 0, canvasY, "Seq1 Assign")
		self.createVcoTitleSection(2 * distanceX - 5, 1, canvasY, "Seq2 Assign")

		# create a line between the two sections
		lineCanvasWidth = mainSpaceX

		lineCanvasX = np.mean([self.vcoRots[0].centerAbs[0], self.vcoRots[1].centerAbs[0]]) - mainSpaceX / 2
		lineCanvasY = offset_y - 15

		linecanvasHeight = self.vcoRots[-1].centerAbs[1] - lineCanvasY + 50

		lineCanvas = tk.Canvas(self.back, width=lineCanvasWidth, height=linecanvasHeight, highlightthickness=0, bg='white')
		lineCanvas.place(x=lineCanvasX, y=lineCanvasY)
		lineCanvas.create_line(mainSpaceX / 2, 0, mainSpaceX / 2, linecanvasHeight)
		lineCanvas.create_line(0, 0, mainSpaceX, 0)

		waveSelectW = 8
		waveCanvasH = 3 * waveSelectW + 1
		waveCanvasW = 2 * waveSelectW + 1

		waveCanvas1X = self.vcoRots[0].centerAbs[0] - self.vcoRots[0].width
		waveCanvas1Y = self.vcoRots[0].centerAbs[1] - waveCanvasH/2

		waveCanvas2X = self.vcoRots[1].centerAbs[0] + self.vcoRots[1].width - waveCanvasW

		waveCanvas1 = tk.Canvas(self.back, width=waveCanvasW, height=waveCanvasH, highlightthickness=0, bg='white')
		waveCanvas1.place(x=waveCanvas1X, y=waveCanvas1Y)
		waveCanvas2 = tk.Canvas(self.back, width=waveCanvasW, height=waveCanvasH, highlightthickness=0, bg='white')
		waveCanvas2.place(x=waveCanvas2X, y=waveCanvas1Y)

		wave1 = WaveSelect(waveCanvas1, waveSelectW, [waveSelectW, 0], 1, 0)
		wave2 = WaveSelect(waveCanvas2, waveSelectW, [0, 0], -1, 1)

	def createVcoTitleSection(self, width, rotID, offset_y, title):
		sectionWidth = width
		titleheight = 20
		titleX = (self.vcoRots[rotID].centerAbs[0] - width / 2)
		# titleX = offset_x
		titleY = offset_y - titleheight - 5

		titleCanvas = tk.Canvas(self.back, width=sectionWidth, height=titleheight, highlightthickness=0, bg='white')
		titleCanvas.place(x=titleX, y=titleY)
		titleID = titleCanvas.create_text(0, 0, text=title)
		titleCanvas.itemconfig(titleID, font=("Purisa", 8))
		titleCanvas.coords(titleID, (sectionWidth / 2, 10))
		bbox = titleCanvas.bbox(titleID)

		# print(bbox)
		bbox = [bbox[0] - 1, bbox[1] - 1, bbox[2], bbox[3]]

		titleCanvas.create_line(0, 10, bbox[0] - 3, 10)
		titleCanvas.create_line(bbox[2] + 3, 10, sectionWidth, 10)

		titleCanvas.create_rectangle(bbox, fill='black')
		titleCanvas.itemconfig(titleID, fill='white')
		titleCanvas.tag_raise(titleID)

	def createFilterRot(self, widthMain, pos, ID, titles):
		self.filterRots.append(Rotary(self.back, widthMain, pos, ID, self))
		self.filterRots[-1].dictToSend['rottype'] = 'filterrot'
		self.filterRots[-1].dictToSend['rotid'] = ID
		title = titles[ID]

		if title == 'Q':
			self.filterRots[-1].valueMax = 1000
			self.filterRots[-1].valuesTablePrompt = [i * 15. / self.filterRots[-1].valueMax for i in range(self.filterRots[-1].valueMax)]
			# self.r[-1].valuesTablePrompt = np.arange(10)
			self.filterRots[-1].param = title
			title = 'Reso'
			self.filterRots[-1].valuesTableSend = self.filterRots[-1].valuesTablePrompt
		elif title == 'fc':

			# debug : commenting these three lines

			# self.filterRots[-1].valueMax = 12700
			# self.filterRots[-1].valuesTablePrompt = [i * 127 / self.filterRots[-1].valueMax for i in range(self.filterRots[-1].valueMax)]
			# self.filterRots[-1].valuesTableSend = self.filterRots[-1].valuesTablePrompt

			self.filterRots[-1].param = title
			title = 'Cutoff'

		elif 'filter' in title:
			self.filterRots[-1].param = title
			title = title[:1]

		if COLORS:
			self.filterRots[-1].canvas.itemconfig(self.rythmRots[-1].arc, outline='DarkOrchid1')

		self.filterRots[-1].setTitle(title)

		if self.filterRots[-1].param == "":
			self.filterRots[-1].param = title

	def createFilterSection(self):
		offset_x = 400 - 20
		offset_y = 430

		width = 40
		widthMain = 60

		distanceX = 60
		distanceY = 70
		distanceXMain = 80

		mainSpaceX = 10

		titles = ['fc', 'Q', 'EG Amount']
		titles.extend(['A filter', 'D filter'])

		x0 = offset_x
		y0 = offset_y + distanceY - (distanceY - width)/2 - widthMain/2
		pos = (x0, y0)

		# distanceY - (distanceY - width)/2 - widthMain/2

		ID = 0
		self.createFilterRot(widthMain, pos, ID, titles)

		for i in range(2):
			for j in range(2):
				ID = j + 2 * i + 1

				pos = (offset_x + j * distanceX + distanceXMain, offset_y + i * distanceY)
				self.createFilterRot(width, pos, ID, titles)

		widthSection = 2 * distanceX + distanceXMain

		self.createFilterTitleSection(widthSection, offset_x, offset_y, 'Filter')

	def createFilterTitleSection(self, width, offset_x, offset_y, title):
		sectionWidth = width
		titleheight = 20
		# titleX = (self.vcoRots[rotID].centerAbs[0] - width / 2)
		titleX = offset_x
		titleY = offset_y - titleheight - 5

		titleCanvas = tk.Canvas(self.back, width=sectionWidth, height=titleheight, highlightthickness=0, bg='white')
		titleCanvas.place(x=titleX, y=titleY)
		titleID = titleCanvas.create_text(0, 0, text=title)
		titleCanvas.itemconfig(titleID, font=("Purisa", 8))
		titleCanvas.coords(titleID, (sectionWidth / 2, 10))
		bbox = titleCanvas.bbox(titleID)

		# print(bbox)
		bbox = [bbox[0] - 1, bbox[1] - 1, bbox[2], bbox[3]]

		titleCanvas.create_line(0, 10, bbox[0] - 3, 10)
		titleCanvas.create_line(bbox[2] + 3, 10, sectionWidth, 10)

		titleCanvas.create_rectangle(bbox, fill='black')
		titleCanvas.itemconfig(titleID, fill='white')
		titleCanvas.tag_raise(titleID)

	def createEnvRot(self, widthMain, pos, ID, titles):
		self.envRots.append(Rotary(self.back, widthMain, pos, ID, self))
		self.envRots[-1].dictToSend['rottype'] = 'envrot'
		self.envRots[-1].dictToSend['rotid'] = ID
		title = titles[ID]

		if COLORS:
			self.envRots[-1].canvas.itemconfig(self.rythmRots[-1].arc, outline='SpringGreen3')

		self.envRots[-1].setTitle(title)

		if self.envRots[-1].param == "":
			self.envRots[-1].param = title

	def createEnvSection(self):
		offset_x = 200 + 35
		offset_y = 430

		width = 40
		widthMain = 60

		distanceX = 60
		distanceY = 70

		titles = ['A', 'D']
		titles.extend(['S', 'R'])

		x0 = offset_x
		y0 = offset_y + distanceY - (distanceY - width)/2 - widthMain/2

		for i in range(2):
			for j in range(2):
				ID = j + 2 * i

				pos = (offset_x + j * distanceX, offset_y + i * distanceY)
				self.createEnvRot(width, pos, ID, titles)

		widthSection = 2 * distanceX

		self.createFilterTitleSection(widthSection, offset_x, offset_y, 'Env')

	def createEnvTitleSection(self, width, offset_x, offset_y, title):
		sectionWidth = width
		titleheight = 20
		# titleX = (self.vcoRots[rotID].centerAbs[0] - width / 2)
		titleX = offset_x
		titleY = offset_y - titleheight - 5

		titleCanvas = tk.Canvas(self.back, width=sectionWidth, height=titleheight, highlightthickness=0, bg='white')
		titleCanvas.place(x=titleX, y=titleY)
		titleID = titleCanvas.create_text(0, 0, text=title)
		titleCanvas.itemconfig(titleID, font=("Purisa", 8))
		titleCanvas.coords(titleID, (sectionWidth / 2, 10))
		bbox = titleCanvas.bbox(titleID)

		# print(bbox)
		bbox = [bbox[0] - 1, bbox[1] - 1, bbox[2], bbox[3]]

		titleCanvas.create_line(0, 10, bbox[0] - 3, 10)
		titleCanvas.create_line(bbox[2] + 3, 10, sectionWidth, 10)

		titleCanvas.create_rectangle(bbox, fill='black')
		titleCanvas.itemconfig(titleID, fill='white')
		titleCanvas.tag_raise(titleID)

	def createOtherRots(self):

		widthSection = 235 - 50

		gridX = 2
		gridY = 1

		offset_x = 22
		offset_y = 430

		# distanceX = widthSection/2
		distanceY = 70
		width = 40

		widthMain = 60
		widthC = widthMain + 20

		posY = offset_y + distanceY - (distanceY - width) / 2 - widthMain / 2

		spaceX = (widthSection - 2 * widthC)/4
		posX = offset_x + spaceX

		distanceX = widthC + 2 * spaceX

		otherRotsColors = dict()
		otherRotsColors['Vol'] = 'DeepSkyBlue3'
		otherRotsColors['Tempo'] = 'DeepSkyBlue3'

		for i in range(gridY):
			for j in range(gridX):

				pos = (posX + j * distanceX, posY)
				ID = i * gridX + j
				self.r.append(Rotary(self.back, widthMain, pos, ID, self))
				self.r[-1].dictToSend['rotid'] = ID
				try:
					title = self.titleOtherRot[ID]
				# print(title[:4], title[:4] == "Step")
				except IndexError:
					title = 'Undef'

				self.r[-1].setTitle(title)
				if title in otherRotsColors.keys():
					self.r[-1].canvas.itemconfig(self.r[-1].arc, outline=otherRotsColors[title])
				if self.r[-1].param == "":
					self.r[-1].param = title

		self.createOtherTitleSection(widthSection, offset_x, offset_y, 'General')

	def createOtherTitleSection(self, width, offset_x, offset_y, title):
		sectionWidth = width
		titleheight = 20
		# titleX = (self.vcoRots[rotID].centerAbs[0] - width / 2)
		titleX = offset_x
		titleY = offset_y - titleheight - 5

		titleCanvas = tk.Canvas(self.back, width=sectionWidth, height=titleheight, highlightthickness=0, bg='white')
		titleCanvas.place(x=titleX, y=titleY)
		titleID = titleCanvas.create_text(0, 0, text=title)
		titleCanvas.itemconfig(titleID, font=("Purisa", 8))
		titleCanvas.coords(titleID, (sectionWidth / 2, 10))
		bbox = titleCanvas.bbox(titleID)

		# print(bbox)
		bbox = [bbox[0] - 1, bbox[1] - 1, bbox[2], bbox[3]]

		titleCanvas.create_line(0, 10, bbox[0] - 3, 10)
		titleCanvas.create_line(bbox[2] + 3, 10, sectionWidth, 10)

		titleCanvas.create_rectangle(bbox, fill='black')
		titleCanvas.itemconfig(titleID, fill='white')
		titleCanvas.tag_raise(titleID)

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

	def rythmButtonAction(self, ID):
		self.rythmButtons[ID].toggle()

	def vcoButtonAction(self, ID):
		self.vcoButtons[ID].toggle()

	def donothing(self):
		filewin = tk.Toplevel(self.root)
		button = tk.Button(filewin, text="Do nothing button", command=filewin.destroy, highlightthickness=0)
		button.bind("<Return>", lambda event: filewin.destroy())
		button.focus_set()
		button.pack()

	def noteOn(self, ID, step):
		for r in self.rythmRots:
			try:
				seqN = r.dictToSend['seqid']
				# print(r.param)
				# print(seqN)
				if seqN == ID:
					# print(r.param)
					# print("Gui : param[4] = ", r.param[4])
					# print("Gui : str(step+1) = ", str(step+1))
					if r.dictToSend['stepid'] == step+1:
						r.noteOn()
			except KeyError:
				pass

	def noteOff(self, ID, step):
		for r in self.rythmRots:
			try:
				seqN = r.dictToSend['seqid']
				if seqN == ID:
					if r.dictToSend['stepid'] == step+1:
						r.noteOff()
			except KeyError:
				pass

	def checkQueue(self):
		try:
			message = events.get(block=False)
			if isinstance(message, Event):
				self.change(message)
		except queue.Empty:
			pass

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
			self.applyToGui(message.value, message.param)

	def applyToGui(self, valuesDict, key):
		if 'value' in valuesDict.keys():
			value = valuesDict['value']
		else:
			value = None
		if valuesDict['type'] != 'rot':
			self.applyToGuiButton(valuesDict, value, key)
		else:
			self.applyToGuiRot(valuesDict, value, key)

	def applyToGuiButton(self, valuesDict, value, key):
		# print(valuesDict)
		if valuesDict['buttontype'] == 'rythmbutton':
			ID = int(valuesDict['buttonid'])
			state = int(valuesDict['state'])
			self.rythmButtons[ID].toggle(state)

		elif valuesDict['buttontype'] == 'vcobutton':
			ID = int(valuesDict['id'])
			state = int(valuesDict['state'])
			self.vcoButtons[ID].toggle(state)

		elif valuesDict['buttontype'] == 'wavebutton':
			ID = int(valuesDict['id'])
			wave = valuesDict['wave']
			# self.gui.vcoButtons[ID].toggle(state)

	def applyToGuiRot(self, valuesDict, value, key):
		ID = valuesDict['rotid']
		if valuesDict['rottype'] == 'generic':
			self.r[ID].setValue(value)

		elif valuesDict['rottype'] == 'rythmrot':
			self.rythmRots[ID].setValue(value)

		elif valuesDict['rottype'] == 'vcorot':
			self.vcoRots[ID].setValue(value)

		elif valuesDict['rottype'] == 'envrot':
			self.envRots[ID].setValue(value)

		elif valuesDict['rottype'] == 'filterrot':
			self.filterRots[ID].setValue(value)
