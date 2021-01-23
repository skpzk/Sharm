from PySide6.QtGui import QPaintEvent
from PySide6 import QtGui, QtCore

from gui.sections.Section import section
from gui.widgets.PatchCordList import PatchCordList
from gui.widgets.Patchpoint import Patchpoint
from gui.widgets.Patchcord import Patchcord
from gui.defs import *

import PySide6.QtWidgets as Qtw
from state.State import State


class Patchbay(Qtw.QWidget):
	def __init__(self, parent: Qtw.QWidget):
		super(Patchbay, self).__init__(parent)

		# self.setTitle("Patchbay")

		box, vbox = section("Patchbay  ")

		grid = Qtw.QGridLayout()

		titlesIn = ["VCO 1", "VCO 1 SUB", "VCO 1 PWM",
		            "VCA", "VCO 2", "VCO 2 SUB", "VCO 2 PWM",
		            "CUTOFF", "PLAY", "RESET", "TRIGGER",
		            # "CUTOFF", "RESET", "TRIGGER",
		            "RHYTHM 1", "RHYTHM 2", "RHYTHM 3", "RHYTHM 4",
		            "CLOCK",
		            "SEQ 1", "SEQ 2"]

		titlesOut = ["VCA", "VCO 1", "VCO 1 SUB 1", "VCO 1 SUB 2",
		             "VCA EG", "VCO 2", "VCO 2 SUB 1", "VCO 2 SUB 2",
		             "VCF EG",
		             "SEQ 1", "SEQ 1 CLK", "SEQ 2", "SEQ 2 CLK", "NOISE",
		             "CLOCK", "SH", "MIDI CLK", "MIDI"]#, "PLAY"]

		titlesIndex = [3, 4,
		               4, 4,
		               4, 1,
		               4, 5,
		               1, 4,
		               2, 0]

		titles = []
		types = []

		self.pps = []

		for i in range(int(len(titlesIndex) / 2)):
			for j in range(titlesIndex[2 * i]):
				titles.append(titlesIn.pop(0))
				types.append('in')
			for j in range(titlesIndex[2 * i + 1]):
				titles.append(titlesOut.pop(0))
				types.append('out')

		for i in range(4):
			for j in range(9):
				ID = i + j * 4
				pp = Patchpoint(self, titles[ID], types[ID])
				# pp.setStyleSheet("qproperty-fixedSize: 36; background-color: white;")
				grid.addWidget(pp, j, i)
				self.pps.append(pp)

		vbox.setStretch(0, 0)
		vbox.addLayout(grid, 1)

		text = """<html><head/><body><p>IN / <span style=" color:%s;background-color:%s">OUT</span></p></body></html>""" %(backgroundColor, pointColor)

		# print("text = ", text)

		fontsize = .38 * 36 / 2
		# print("fontsize = ", fontsize)


		label = Qtw.QLabel(text)
		label.setAlignment(QtCore.Qt.AlignCenter)
		font = label.font()
		font.setPointSizeF(fontsize)
		label.setFont(font)
		vbox.addWidget(label)

		self.setLayout(vbox)

		self.pcs = PatchCordList()

		self.displayPp = "all"  # or "in" or "out"

		self.resizePcs()

		self.checkState()

	def findPp(self, inppName: str, outppName: str):
		inpp = outpp = None
		for pp in self.pps:
			if pp.title.replace(" ", "").lower() == inppName and pp.io == "in":
				inpp = pp
			if pp.title.replace(" ", "").lower() == outppName and pp.io == "out":
				outpp = pp
		return inpp, outpp

	def checkState(self):
		for inppName, value in State().params['patchbay'].items():
			for outppName in value:
				self.newPcFromPpNames(inppName, outppName)

	def newPcFromPpNames(self, inName: str, outName: str):

		inpp, outpp = self.findPp(inName, outName)
		if inpp is not None and outpp is not None:
			self.createPC(inpp)
			self.pcs.last().setPoints(endpp=outpp)
			self.pcs.last().connectPC()
			self.pcs.last().isHovered = False
			self.displayPp = 'all'

	def createPC(self, pp: Patchpoint):
		pc = Patchcord(self)
		pc.setPoints(startpp=pp, pos=pp)

		self.displayPp = pc.endPointIo

		self.pcs.add(pc)

	def movePC(self, pc, pp):
		self.pcs.add(pc)
		self.pcs.last().disconnectPC(pp)
		self.displayPp = self.pcs.last().endPointIo
		self.repaint()

	def moveLastPC(self, pos: QtCore.QPoint):
		self.pcs.last().setPoints(pos=pos)
		# print(type(pos))
		self.repaint()

	def disposeOfLastPc(self):
		pc = self.pcs.last()
		self.pcs.remove(pc)
		pc.deleteFromPpLists()
		pc.deleteLater()
		self.displayPp = 'all'

	def findReleasePp(self, pos: QtCore.QPoint):
		isPpFound = False
		pprelease = None
		for pp in self.pps:
			isPpFound, pprelease = pp.isMouseReleaseOnPP(pos)
			if isPpFound:
				break

		if not isPpFound:
			self.disposeOfLastPc()
		else:
			if pprelease.io != self.pcs.last().endPointIo:
				self.disposeOfLastPc()
			else:
				self.pcs.last().setPoints(endpp=pprelease)
				self.pcs.last().connectPC()
				self.displayPp = 'all'

		self.repaint()

	def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
		self.resizePcs()

	def resizePcs(self):
		for pc in self.pcs:
			pc.resize(self.size())

	def paintEvent(self, event: QPaintEvent) -> None:

		opt = Qtw.QStyleOption()
		opt.initFrom(self)
		painter = QtGui.QPainter(self)

		# painter.setBackgroundMode(Qt.TransparentMode)
		s = self.style()

		s.drawPrimitive(Qtw.QStyle.PE_Widget, opt, painter, self)

		self.resizePcs()


if __name__ == "__main__":
	from gui.minimal_window_for_test import Window
	from PySide6.QtWidgets import QApplication
	# from PySide6 import QtCore
	app = QApplication()

	window = Window()
	window.show()

	patchbay = Patchbay(window)

	# inpp, outpp = patchbay.findPp('vco1', 'vco2')

	patchbay.newPcFromPpNames('vco1', 'vco2')


	window.setCentralWidget(patchbay)

	window.resize(QtCore.QSize(300, 500))

	window.update()
	app.exec_()
