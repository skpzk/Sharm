import tkinter as tk
# from Dev.DebugUtils import *


class ResizingCanvas(tk.Canvas):
	def __init__(self, parent, **kwargs):
		tk.Canvas.__init__(self, parent, **kwargs)
		self.bind("<Configure>", self.on_resize)
		self.height = self.winfo_reqheight()
		self.width = self.winfo_reqwidth()

	def on_resize(self, event):
		# determine the ratio of old width/height to new width/height
		size = min(event.width, event.height)
		# historyprint("Resize", history=5)
		wscale = float(size) / self.width
		hscale = float(size) / self.height
		self.width = size
		self.height = size
		# resize the canvas
		self.config(width=self.width, height=self.height)
		# rescale all the objects tagged with the "all" tag
		self.scale("all", 0, 0, wscale, hscale)
