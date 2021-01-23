from PySide6 import QtCore

from gui.defs import *
from gui.widgets.SectionLabel import SectionLabel
from PySide6 import QtWidgets as Qtw


def section(sectiontitle):
	box = Qtw.QWidget()
	widgetConf(box)

	label = SectionLabel(sectiontitle)
	label.setAlignment(QtCore.Qt.AlignCenter)
	widgetConf(label)

	vbox = Qtw.QVBoxLayout()
	layoutConf(vbox)
	vbox.addWidget(label)

	return box, vbox