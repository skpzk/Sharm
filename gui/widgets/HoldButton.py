from PySide6 import QtGui, QtCore

from gui.widgets.Buttons import Button
from state.State import State


class HoldButton(Button):
	def __init__(self, title):
		super(HoldButton, self).__init__(title)
		self.installEventFilter(self)
		self.grabGesture(QtCore.Qt.TapAndHoldGesture)

		self.held = False
		self._heldColor = QtGui.QColor("blue")
		self._hasHeldColor = True

		self.clicked.connect(self.removeHeld)
		self.pressed.connect(self.removeHeld)

		self.ignoreFirstClick = 0

	def removeHeld(self):
		# print("remove held called")
		self.held = False
		# self.pressedColor = Button("").pressedColor

	def _getHeldColor(self):
		# print("getfixedSize called")
		return self._heldColor

	def _setHeldColor(self, color: str):
		# print("setfixedSize called")
		self._heldColor = QtGui.QColor(color)
		self._hasHeldColor = True

	holdColor = QtCore.Property(str, _getHeldColor, _setHeldColor)

	def checkState(self):
		try:
			# self.setValue(State.params[self._stateKey] * self.maximum())
			checked = State.params[self._stateKey] * 1
			self.setChecked(checked == 1)
			if checked == .5:
				self.held = True
		# mprint("key =", self._stateKey, "Statevalue = ", State.params[self._stateKey], "value = ", self.value())
		except KeyError:
			# print("Key error : key =", self._stateKey)
			self.warnState()

	def warnStateHeld(self):
		State.params[self._stateKey] = .5
		# print("key =", self._stateKey, "Statevalue = ", State.params[self._stateKey], "value = ", self.isChecked(), "Warning state")


	def mouseReleaseEvent(self, e: QtGui.QMouseEvent) -> None:
		if self.held:
			pass
			self.repaint()
		else:
			super(Button, self).mouseReleaseEvent(e)

	def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
		# print("event received")
		if event.type() == QtCore.QEvent.Gesture:
			# print("Tap and hold detected")
			self.held = True
			# self.bgColor = QtGui.QColor("red")
			# self.ignoreFirstClick = 0
			self.setChecked(True)
			# self.pressedColor = QtGui.QColor("red")
			self.setDown(False)
			self.warnStateHeld()
			self.repaint()
			return True
		return False
