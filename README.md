# lecroy
Lecroy oscilloscope class to automate configuration, measurements and screen capture.
"update_signal_offset" added to measure signal and read vertical scale in order to position the signal at a specified horitontal division on the display.
If your signal is the voltage of a resistor and the current can vary, calling the "update_signal_offset" will re-position that signal.

Added get_analog_channel_setup(), get_digital_channel_setup(), and get_measurement_setup() which will return the dictionaries of the present settings on the oscilloscope. This is useful when you already have a manual setting and want to document it for use later (say in a script).
