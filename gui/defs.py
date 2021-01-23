coulours = dict()
coulours['seq'] = "#00b2ee"
coulours['rhythm'] = "#ff0000"
coulours['vco1'] = "#00ee76"
coulours['vco2'] = "#ff8c00"
coulours['general'] = "#009acd"
coulours['env'] = "#00cd66"
coulours['filter'] = "#bf3eff"



darkTheme = True
# darkTheme = False
if darkTheme:
	backgroundColor = "#111111"
	buttonBackground = "#919191"
	# buttonBackground = "red"
	pointColor = "white"
	barsColor = "#aaaaaa"
	sectionLabelColor = backgroundColor
	ppColor = backgroundColor
else:
	backgroundColor = "white"
	buttonBackground = "white"
	pointColor = "black"
	barsColor = "black"
	sectionLabelColor = "black"
	ppColor = "black"


def knobDefaultStyleSheet(color: str, bgColor: str = "transparent"):
	# return "background-color: " + bgColor + ";color: #000000; qproperty-ringColor: " + coulours[color] + ";"
	return "background-color: " + bgColor + ";color: " + pointColor + ";qproperty-ringColor: " + coulours[color] + ";"

# def knobDefaultStyleSheet(color: str, bgColor: str = "white"):
# 	return "color: #000000;qproperty-ringColor: " + coulours[color] + ";"

def buttonDefaultStyleSheet():
	styleSheet = """
		Button{
			background-color: buttonBackground;
			border: 1px solid #aaa;
			color: black;
		}
		Button::Checked{
			background-color: black;
			border: 0px;
			color: white;
		}
		Button::Pressed{
			background-color: #343434;
			border: 0px;
		}
		HoldButton{
			qproperty-holdColor: orange;
		}
		"""

	styleSheet = styleSheet.replace("buttonBackground", buttonBackground)
	return styleSheet

def mainWindowStyleSheet():
	styleSheet = """
	QMainWindow{
	background-color: backgroundColor;
	}
	QGroupBox{
		border: 0px solid #414141;
		border-top: 1px solid pointColor;
		margin: 0px;
		margin-top: 10px;
		padding: 0px;
		padding-top: 0px;}
	QGroupBox::title{
		subcontrol-origin: margin;
		subcontrol-position: top;
		padding: 0 10px 0 10px;
		padding: 0 0px 0 0px;
		background-color: pointColor;
		font-size: 500pt;
		color: backgroundColor
	}
	Radio{
		color: pointColor;
	}
	QLabel{
		color: pointColor;
	}
	SectionLabel{
		color: sectionLabelColor;
		qproperty-barsColor: barsColorName;
	}
	WaveSlider{
		color: pointColor;
	}
	Patchpoint{
		qproperty-fixedSize: 36;
		color: pointColor;
		background-color: backgroundColor;
		qproperty-ppColor: ppColorName;
	}
	"""


	styleSheet = styleSheet.replace("backgroundColor", backgroundColor)
	styleSheet = styleSheet.replace("pointColor", pointColor)
	styleSheet = styleSheet.replace("barsColorName", barsColor)
	styleSheet = styleSheet.replace("sectionLabelColor", sectionLabelColor)
	styleSheet = styleSheet.replace("ppColorName", ppColor)

	# print(styleSheet)

	return styleSheet

def layoutConf(layout):
	layout.setContentsMargins(0, 0, 0, 0)
	layout.setSpacing(0)

def widgetConf(widget):
	widget.setContentsMargins(0, 0, 0, 0)
