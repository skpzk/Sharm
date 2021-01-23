import numpy as np
from PySide6 import QtCore


def distance(a: QtCore.QPoint, b: QtCore.QPoint):
	return np.sqrt(np.power(a.x() - b.x(), 2) + np.power(a.y() - b.y(), 2))
