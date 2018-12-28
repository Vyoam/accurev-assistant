# accurev-assistant
Python script to complement the relatively faster CLI of AccuRev with some basic GUI

--- --- ---

Summary:

AccuRev’s GUI is somehow much slower than its CLI in many cases. Here is a tool which leverages the speed of CLI and provides some basic GUI which will help in most day to day tasks.
It basically parses the result lists (modified, pending, kept etc.) and allows you to select elements, which you want to keep, promote, revert et al. You can also see all the background details in the console.
You need Python to run the tool. (Full usage details below)
Currently, it lacks support for viewing history, navigating to other streams, resolving conflicts, among others.


Installation:

1.	Download the script: https://raw.githubusercontent.com/Vyoam/accurev-assistant/master/accurev.py
Or better, clone the repo: https://github.com/Vyoam/accurev-assistant

2.	Verify the system requirements below and invoke the script from console: accurev.py OR python accurev.py – whatever your system supports
3.	With respect to the the GUI screenshot above, select command at the upper menu (e.g. kept, modified) to list out the required elements. Then select desired elements and apply the bottom command (e.g. revert, promote) to them.


System Requirements:

Python 2.7.11 with Tk enabled
AccuRev command line accessibility


Windows steps:

https://www.python.org/downloads/
Install with ‘Tcl/Tk’, ‘Add to Path’, ‘Register Extensions’ enabled 


Linux steps:

Have Python in version 2.7.11

To install Tkinter, use…
sudo apt-get install python-tk
(or the relevant pakcage manager)
