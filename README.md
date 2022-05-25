# lecroy
![picture](https://prnewswire2-a.akamaihd.net/p/1893751/sp/189375100/thumbnail/entry_id/0_glmpkpp2/def_height/2700/def_width/2700/version/100012/type/1)


Lecroy oscilloscope class to automate configuration, measurements and screen capture.
"update_signal_offset" added to measure signal and read vertical scale in order to position the signal at a specified horitontal division on the display.
If your signal is the voltage of a resistor and the current can vary, calling the "update_signal_offset" will re-position that signal.

Added get_analog_channel_setup(), get_digital_channel_setup(), get_measurement_setup(), get_trigger_setup() and get_horizontal_scale() which will return the dictionaries of the present settings on the oscilloscope. This is useful when you already have a manual setting and want to capture/document it for use later (say in a script).
