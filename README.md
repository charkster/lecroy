# lecroy
Lecroy oscilloscope class to automate configuration, measurements and screen capture.
"update_signal_offset" added to measure signal and read vertical scale in order to position the signal at a specified horitontal division on the display.
If your signal is the voltage of a resistor and the current can vary, calling the "update_signal_offset" will re-position that signal.
