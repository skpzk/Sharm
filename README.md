# Sharmv2
Sharmv2 is a recreation of Sharm, with knowledge acquired during development of Marble

I am currently coding a brand new interface with Qt instead of Tkinter.
The goal is to have a resizeable interface with improved and antialiased widgets.

In addition, the audio lib is now modular, to ease the integration of a Patchbay. 
The oscillators are also improved, with an implementation of the blep algorithm in order to remove aliasing with high frequencies.

To do before release:
- finish patchbay
- solve bug with multiple patchcords : can't reproduce bug
- solve bug with dict in patchbay : seems to be solved
- a bit of cleaning and commenting
- don't give focus to knob 1 on startup
- bug with clock : sometimes a delay is added btw two steps : why ?

tbd later:
- make wheels package for cython modules (and maybe branch without cython) : tbd later
- implement blep or blit for tri wave : tbd later

Finishing Patchbay:
- play in : replace with s&h linked to clock
- reset in
- trigger out

Done: 
- clk seq 1 and 2 : replace with square wave changing value on each trigger
- seq1&2 in

