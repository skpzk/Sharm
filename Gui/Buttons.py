import tkinter as tk
from State import State
from abc import ABC
from Gui import Gui


class Button(ABC):
	def __init__(self, back, rel, seqID, buttonID):
		self.state = 1
		self.button = None
		self.seqID = seqID
		self.buttonID = buttonID

		self.dictToSend = dict()
		self.dictToSend['type'] = 'button'
		self.dictToSend['state'] = self.state
		self.dictToSend['seqid'] = self.seqID
		self.dictToSend['buttonID'] = self.buttonID

		self.eventName = ""

		self.back = back
		relx, rely, relw, relh = rel

		self.canvas = tk.Canvas(self.back, highlightthickness=0)
		self.canvas.place(relx=relx, rely=rely, relwidth=relw, relheight=relh)
		self.canvas.configure(bg=Gui.mainColor)

	def toggle(self, **kwargs):
		try:
			state = kwargs['state']
		except KeyError:
			state = None
		try:
			sendEvent = kwargs['sendEvent']
		except KeyError:
			sendEvent = True

		if state:
			self.state = - state + 1
		if self.state == 1:
			# self.button.config(relief=tk.SUNKEN)
			self.button.config(bg='black')
			self.button.config(fg='white')
			self.button.config(activebackground='grey25')
			self.button.config(activeforeground='white')
			self.state = 0
			self.dictToSend['state'] = self.state
			if sendEvent:
				State.events.put(State.Event(self.eventName, self.dictToSend))
		else:
			# self.button.config(relief=tk.RAISED)
			self.button.config(bg='white')
			self.button.config(fg='black')
			self.button.config(activebackground='gray75')
			self.button.config(activeforeground='black')
			self.state = 1
			self.dictToSend['state'] = self.state
			if sendEvent:
				State.events.put(State.Event(self.eventName, self.dictToSend))


class RythmButton(Button):
	def __init__(self, back, rel, buttonrel, seqID, clkID):
		i = clkID - 1
		j = seqID - 1
		ID = i + j * 4
		# print(ID)
		super().__init__(back, rel, seqID, ID)

		self.seqID = seqID
		self.clkID = clkID
		self.button = tk.Button(self.canvas, text="Seq" + str(seqID),
		                        bg='white', activebackground='white',
		                        activeforeground='black', highlightthickness=1, relief=tk.FLAT)
		buttonRelW, buttonRelH = buttonrel
		self.button.place(relwidth=buttonRelW, relheight=buttonRelH, relx=0.5, rely=0.5, anchor=tk.CENTER)
		self.button.config(font=("Purisa", 8))

		self.dictToSend['clkid'] = self.clkID
		self.dictToSend['buttontype'] = 'rhythm'

		self.eventName = 'callbackClk' + str(self.seqID) + str(self.clkID)

		self.toggle(state=1, sendEvent=False)

		self.button.config(command=self.toggle)


class VcoButton(Button):
	def __init__(self, back, rel, buttonrel, ID, voiceID, titles):
		if ID < 3:
			seqID = 1
		else:
			seqID = 2
		super().__init__(back, rel, seqID, ID)

		self.button = tk.Button(self.canvas, text=titles[ID].capitalize(),
		                        bg='white', activebackground='white',
		                        activeforeground='black', highlightthickness=1, relief=tk.FLAT)
		buttonRelW, buttonRelH = buttonrel
		self.button.place(relwidth=buttonRelW, relheight=buttonRelH, relx=0.5, rely=0.5, anchor=tk.CENTER)
		self.button.config(font=("Purisa", 8))

		self.voiceID = voiceID
		self.title = titles[ID]

		self.toggle(state=1, sendEvent=False)

		self.dictToSend['id'] = self.buttonID
		self.dictToSend['voiceid'] = self.voiceID

		self.dictToSend['buttontype'] = 'vco'

		self.eventName = 'assign' + str(self.seqID) + str(self.buttonID)

		self.button.config(command=self.toggle)
