# pynuphase
simple python tools for analyzing rootified nuphase data

Requires nuphaseroot  https://github.com/vPhase/nuphaseroot

Specify nuphaseroot install directory and data location in setup.py

Basic detector properties defined in detector.py

A quick look at the distribution of SPiceCore pulses is provided in examples/spiceCore.py. 
Run as:
```
python -m examples.spiceCore
```

A simple event viewer can be run as:
```
python event_viewer.py [run] [root_tree_entry]
```
![alt text](https://github.com/vPhase/pynuphase/blob/master/doc/frun660entry1.png)

