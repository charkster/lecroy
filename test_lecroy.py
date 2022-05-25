#!/usr/bin/python

import time
import pyvisa
from   lecroy import lecroy

rm = pyvisa.ResourceManager()
#print rm.list_resources()
lecroy = lecroy(pyvisa_instr=rm.open_resource('USB0::0x0000::0x0000:C123456::INSTR'))

# label, ver_scale, ver_offset, bw, coupling
analog_channels = {
    1: ('COOL_V1',      0.2,   -10,  '20MHz', 'DC1M'),
    2: ('NASTY_V2',     0.5,  -4.9,  '20MHz', 'DC1M'),
    3: ('FAVORITE_V3',    2,   -10,  '20MHz', 'DC1M'),
    4: ('OLD_V4',         2,    -8,  '20MHz', 'DC1M'),
    5: ('LITTLE_I1',      2,   3.0,  '20MHz', 'DC'),
    6: ('BIGGER_I2',      2,   1.0,  '20MHz', 'DC'),
    7: ('IMPORTANT_I3',   2,  -0.5,  '20MHz', 'DC'),
    8: ('ARB_I4',       0.5,  -1.5,  '20MHz', 'DC')
}

# number, label
digital_channels = {
    0: 'cool_name_1',
    1: 'even_better_name_2',
    2: 'the_best_name_3',
    3: 'worst_name_4'
}

measurement_channels = { 1:  ('C1', 'max'),
                         2:  ('C1', 'level@x'),
                         3:  ('C2', 'max'),
                         4:  ('C2', 'level@x'),
                         5:  ('C3', 'max'),
                         6:  ('C3', 'level@x'),
                         7:  ('C5', 'max'),
                         8:  ('C6', 'max'),
                         9:  ('C7', 'max'),
                         10: ('C8', 'max'),
                         11: ('C8', 'level@x'),
                         12: ('C8', 'level@x') }
						 
lecroy.reset_scope()
time.sleep(2)
lecroy.set_date_and_time() # use system date and time
lecroy.setGrid('Single')
lecroy.channel_setup(analog_channels, digital_channels)
lecroy.get_analog_channel_setup()
lecroy.get_digital_channel_setup()
hor_scale = 0.2*lecroy.unit_ms
lecroy.horizontal_scale(hor_scale)
lecroy.get_horizontal_scale()
lecroy.measurement_setup(measurement_channels)
lecroy.measurement_levelatx(meas_channel=11, position=-1.0e-6)     #before trigger
lecroy.measurement_levelatx(meas_channel=12, position=1.599992e-3) #last captured value
lecroy.get_measurement_setup()
lecroy.trigger_setup(channel='C4', trig_level=0.25, trig_horizontal=hor_scale * (-3), trig_slope='Positive', trig_mode='Auto')
time.sleep(2)
lecroy.update_signal_offset(analog_channels, 'LITTLE_I1', 0) #adjust the offset for 'LITTLE_I1' signal to be on the center division
lecroy.trigger_setup(channel='C4', trig_level=0.25, trig_horizontal=hor_scale * (-3), trig_slope='Positive', trig_mode='Single')
lecroy.get_trigger_setup()
lecroy.get_screen_image('super_awesome_waveform_12')

max_C1                  = "{:.3f}".format(lecroy.getValueOnChannel('P1', 'value'))
value_C1                = "{:.3f}".format(lecroy.getValueOnChannel('P2', 'value'))
overshoot_C1            = float(max_C1) - float(value_C1)
val_before_trigger_C8   = "{:.2f}".format(lecroy.getValueOnChannel('P11', 'value'))
val_at_end_C8           = "{:.2f}".format(lecroy.getValueOnChannel('P12', 'value'))
max_C8                  = "{:.2f}".format(lecroy.getValueOnChannel('P10', 'value'))
delta_C8                = float(val_at_end_C8) - float(val_before_trigger_C8)
overshoot_C8            = float(max_C8)        - float(val_before_trigger_C8)
