import time

from PySide6.QtCore import QSize

import Sharm
from gui.Window import Window
from PySide6.QtWidgets import QApplication

"""
TDL:
+ verifier pourquoi les notes de 8ji et 8et sont si differentes
+ sequencer is continuous, not dividers
+ add function to set the sequencer range
+ add quantize function
+ issues at the end of cutoff
  solved by clipping fc
+ solve underrun:
  if Audio is multiprocessing instead of multithreading, it doesn't change much
  multiprocessing + gc disable is not better
  solved by putting audio data in a multiprocessing queue : it smooths the run time
+ relocate cython functions in a more appropriate folder
- audio is no longer a thread, remove it ? or rename _run to run ?
+ start sd thread after everything else is initialized : less underruns
+ improve knob interaction
+ create sections for each section in gui
+ create hold state for EGs
- test EG hold in windows
- make a branch for not cython
- deactivate quantize
+ replace saw and sqr by bw limited ones
- improve implementation of polyblep tri

  
To be implemented :
	Patchbay :
	- Play
	- Reset
	- Trigger i/o
	+ Cutoff
	+ Vcf EG
	+ Seq1/2
	- Seq1/2 Clk
	  Tester ! Is composed of triggers for now, maybe we can make a square wave out of it
	+ Clock i/o
	+ undef : random generator !
	Buttons :
	+ Seq1/2 Assign
	+ Reset
	  bug : when releasing reset, the seqs move immediately to the next step
	  solved
	+ EG : now has a hold state (.5 value in State)
		to do :
		+ inhibit seq eg trigger when unlit
		+ hold eg at max values when EG is held
	+ Next
	+ Trigger
	
	


Gui :
+ calculer la taille des widgets dans Window, et transmettre aux widgets:
	une taille mainTitle, une taille subtitle, mainknob, subknob, etc.
+ diminuer distance seq/vco
+ diminuer largeur des radios
+ diminuer police des boutons
+ diminuer police des box seqAssign
+ augmenter distance rhythm et transport
+ ajouter un label pour range et quantize
- modifier la taille de plice du label "IN/OUT"
+ ajouter un titre pour la patchbay
- replace points with pointF
+ double click pour remettre à 0, m pour muter
- les labels vco1 et vco2 ne sont pas alignées avec les knobs
- colorer le texte des rhythms quand ils envoient un pulse

Bugs :
 Patchbay:
 + double click raises an attribute error : maybe ignore double click ?
   solved by recoding patchbay

 - error when closing: "knob already deleted" -> I'm not seeing it anymore, maybe it is ok now ?
 
 + range doesn't initializes properly
 
 + underrun when moving knobs : 
   maybe change State only if the value changes ?
     it is only emitted once, thanks to "self.valueChanged.connect(self.warnState)"
   maybe put state in a different thread ?
   disabling garbage collection seems to have no effect on performance
   solved with a nice multithreading Queue
   
 + filter has bugs when the cutoff is too high
   solved by clipping the highest values of fc at samplerate/2
 
 + quantize JI with cython doesn't work
   baseA != int(freq/440) 
   solved
   
 - bug when deleting multiple patchcords connected to the same patchpoint 
   can't reproduce bug ?
 
 + corrected bug in windows, the +/- character in sharm.state is not recognized as a single char
 
 + bug in windows : program doesn't end
   corrected by adding a timeout on the queue.put method 
   
 + aliasing in saw and sqr with high frequencies
   maybe using a more analog version of saw and sqr would improve that
   using a bandwidth limited sqr removed the issue, BUT as of now, I don't know how to code it fast enough
   solved with a polyblep implementation
   
 + bug in EG held : the color changes when another object is redrawn
 
 + bug :   
     File "/home/stanislas/pdrive/Sharmv2/audioLib/objects/Patchbay.py", line 30, in __call__
     for cvout in self.outs.values():
     RuntimeError: dictionary changed size during iteration
   probly solved by copying dict before entering loop
     edit : not solved, maybe it needs a deepcopy but I can't make it work with deepcopy
   probly solved by blocking pop items while the Pp is used 

 + puzzling bug with reset:
   when pushed just once, the seq moves to the next step after only 2 pulses from the clock
   solved

Improvements:
 - add custom scale to quantize (via a menu)
 - add other temperaments to quantize
 - add a midi interface
"""

"""
####################################
IMPORTANT NOTE :
####################################

sounddevice on its own can't run on windows, it needs portaudio bindings
to install portaudio without too much hassle, use the following line in the venv:

pip install pipwin
pipwin install pyaudio

We cheat by installing pyaudio (which is not required by Sharm) to build portaudio bindings.
But pyaudio can't be installed by pip for some reason. This pipwin command seems to work.
Thanks to Manas Satti at : https://stackoverflow.com/questions/59025702/pyaudio-installation-error-in-python-windows

Now PyAudio works, but not SoundDevice, which is not ideal but an improvement.

UPDATE : 
The crash was caused by jack, uninstalling jack seems to remove the crash.
thanks to sparky-10 at : https://github.com/spatialaudio/python-sounddevice/issues/275
Hum.

####################################
END OF IMPORTANT NOTE
####################################

"""

if __name__ == "__main__":
	app = QApplication()

	sharm = Sharm.Sharm()

	window = Window()
	window.show()

	window.resize(QSize(950, 620))

	time.sleep(0.1)

	sharm.audio.startAudio()

	print("Init done.")


	app.exec_()

	T = sharm.close()
