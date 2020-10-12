#!/usr/bin/python
import datetime

class lecroy():

    # Constructor
    def __init__(self, pyvisa_instr, num_channels=8, debug=False):
        self.scope        = pyvisa_instr  # this is the pyvisa instrument
        self.num_channels = num_channels
        self.debug        = debug

    unit_ms = 10 ** (-3)
    unit_us = 10 ** (-6)

    def get_screen_image(self, path_with_filename='', backcolor='WHITE'):
        # valid backcolor can be either 'WHITE' or 'BLACK'

        self.scope.write("CHDR OFF;HCSU BCKG,%s;HCSU DEV,PNG;HCSU PORT,GPIB;SCDP" % backcolor)
        raw_data = self.scope.read_raw()
        if (path_with_filename == ''):
            path_with_filename = "lecroy_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".png"
        elif '.png' not in path_with_filename:  # append png if not given
            path_with_filename += '.png'
        file_stream = open(path_with_filename, 'wb')
        file_stream.write(raw_data)
        file_stream.close()
        return len(raw_data)

    def trigger_setup(self, channel, trig_level, trig_horizontal, trig_slope, trig_mode):
        """
        Adjusts the parameters of the trigger setup.
        :param channel: Scope channel for trigger. E.g. 'C1', 'D1'.
        :param trig_level: Voltage or current level for trigger. Int or float.
        :param trig_horizontal: Time position for the trigger (with respect to center at 0).
        :param trig_slope: 'Positive', 'Negative', 'Either'
        :param trig_mode: 'Single', 'Normal', 'Auto', 'Stopped'
        :param delay: in seconds, with negative moving to left
        :return:
        """

        self.scope.write('VBS app.Acquisition.Trigger.Type="Edge"')
        self.scope.write('VBS app.Acquisition.Trigger.Source="{0}"'.format(channel))
        self.scope.write('VBS app.Acquisition.Trigger.Edge.Level={0}'.format(trig_level))
        self.scope.write('VBS app.Acquisition.Horizontal.HorOffset={0}'.format(trig_horizontal))
        self.scope.write('VBS app.Acquisition.Trigger.Edge.Slope="{0}"'.format(trig_slope))
        self.scope.write('VBS app.Acquisition.TriggerMode="{0}"'.format(trig_mode))
        if (channel.startswith('C')):
            self.scope.write('VBS app.Acquisition.Trigger.Coupling="AC"'.format(channel))

    def channel_setup(self, analog_ch_dict, digital_ch_dict):
        """
        This adjusts the analog and digital channels of the LeCroy scope, based on the parameters received.
        :param scope: This is the Lecroy scope object
        :param analog_ch_dict: A dictionary that lists all the parameters for the channels. Key is the channel number.
            Values are in this order: label, vertical scale, vertical offset, bandwidth [for voltage probes: '20MHz', '200MHz', 'Full']
        :param digital_ch_dict:
        :return: None

        Example:
            # - label, ver_scale, ver_offset (voltage value not divisions, with center line as 0V), bw, coupling
            analog_channels = {
                1: ('VBUS1', 0.5,   0, '20MHz', 'DC1M'),
                2: ('IBUS1', 0.5,   1, 'Full',  'DC'),
                3: ('VBAT',  1.0, 0.2, '20MHz', 'DC1M'),
                4: ('VDDS',  0.0, 1.0, '20MHz', 'DC1M'),
                5: ('IL1',   1.0,  -1, '20MHz', 'DC'),
                6: ('IL2',  -2.0, 1.0, '20MHz', 'DC'),
                7: ('IL3',   1.0,  -2, '20MHz', 'DC'),
                8: ('',      0.0,  -3, '20MHz', 'DC1M')
            }

            # --- DIGITAL CHANNELS ---
            # key: digital channel; value: channel label
            digital_channels = {
                0: 'vbus1_uv',
                1: 'vbus12bat'
            }
        """
        ch_desc = {
            'label'     : 0,
            'ver_scale' : 1,
            'ver_offset': 2,
            'bw'        : 3,  # '20MHz', 'Full'
            'coupling'  : 4,  # 'DC50', 'Gnd', 'DC1M', 'AC1M'
        }

        # --- Turn off all analog channels ---
        for sweep_channels in range(1, 9):
            self.scope.write('VBS app.Acquisition.C{0}.View=False'.format(sweep_channels))

        # --- Turn on all listed analog channels and set up ---
        for k, v in analog_ch_dict.items():
            self.scope.write('VBS app.Acquisition.C{0}.View=True'.format(k))
            self.scope.write('VBS app.Acquisition.C{0}.ViewLabels=True'.format(k))
            self.scope.write('VBS app.Acquisition.C{0}.LabelsText="{1}"'.format(k, v[ch_desc['label']]))
            self.scope.write('VBS app.Acquisition.C{0}.VerScale={1}'.format(k, v[ch_desc['ver_scale']]))
            self.scope.write('VBS app.Acquisition.C{0}.VerOffset={1}'.format(k, v[ch_desc['ver_offset']]))
            self.scope.write('VBS app.Acquisition.C{0}.BandwidthLimit="{1}"'.format(k, v[ch_desc['bw']]))
            self.scope.write('VBS app.Acquisition.C{0}.Coupling="{1}"'.format(k, v[ch_desc['coupling']]))

        self.scope.write('VBS app.Display.TraceIntensity=100')

        # ***** Digital Channel Section ******************************************************************
        # --- Turn off all digital channels ---
        for sweep_channels in range(0, 16):
            self.scope.write('VBS app.LogicAnalyzer.Digital1.Digital{0}.Value=false'.format(sweep_channels))
        
        # --- Turn on only listed digital channels and set up ---
        for k, v in digital_ch_dict.items():
            self.scope.write('VBS app.LogicAnalyzer.Digital1.Digital{0}.Value=true'.format(k))
            self.scope.write('VBS app.LogicAnalyzer.Digital1.CustomBitName{0}.Value="{1}"'.format(k, v))
        
        self.scope.write('VBS app.LogicAnalyzer.Digital1.View=true')
        self.scope.write('VBS app.LogicAnalyzer.Digital1.VerPosition=4.00')
        self.scope.write('VBS app.LogicAnalyzer.Digital1.GroupHeight=1.00')
        self.scope.write('VBS app.LogicAnalyzer.Digital1.Labels="CUSTOM"')
        # ***** End Digital Channel Section **************************************************************

    def trigger_force(self):
        # Force a trigger event (when the scope is in the ready state)
        self.scope.write('FORCE_TRIGGER')

    def horizontal_scale(self, scale=1E-3):
        self.scope.write('TDIV %e' % scale)
        self.scope.write('app.Acquisition.Horizontal.Maximize = "MODE"')

    def set_date_and_time(self, year=None, month=None, day=None, hour=None, minute=None, second=None):
        # any part of the date or time is not given, system date and time for the missing part will be used
        if (year is None):
            year =  datetime.datetime.now().year
        if (month is None):
            month =  datetime.datetime.now().month
        if (day is None):
            day =  datetime.datetime.now().day
        if (hour is None):
            hour =  datetime.datetime.now().hour
        if (minute is None):
            minute =  datetime.datetime.now().minute
        if (second is None):
            second =  datetime.datetime.now().second
        self.scope.write("VBS app.Utility.DateTimeSetup.Year = {0}".format(year))
        self.scope.write("VBS app.Utility.DateTimeSetup.Month = {0}".format(month))
        self.scope.write("VBS app.Utility.DateTimeSetup.Day = {0}".format(day))
        self.scope.write("VBS app.Utility.DateTimeSetup.Hour = {0}".format(hour))
        self.scope.write("VBS app.Utility.DateTimeSetup.Minute = {0}".format(minute))
        self.scope.write("VBS app.Utility.DateTimeSetup.Second = {0}".format(second))
        self.scope.write("VBS app.Utility.DateTimeSetup.Validate")

    def measurement_setup(self, meas_dict):
        """
        Sets up the parameters for creating measurements on the scope.
        :param scope:
        :param meas_dict:
            channel: e.g. 'C1', 'D1'
            measurement: common measurements: 'ampl', 'cycles', 'delay', 'ddelay' [2 sources], 'duty cycle'??, 'duty@lv',
            'edge@lv', 'fall8020', 'fall', 'first'??,'freq', 'last'??,'lvl@x', 'max', 'mean', 'median', 'min,
            'pkpk', 'phase', 'rise2080', 'Rise Time', 'RMS', 'slew', 'time@lvl', 'Width', 'wid@lvl', 'X@max', 'X@min'
            - See operation manual for complete list
        :return:

        Example:
            To show measurements on scope:
                # channel || measurement
                # key refers to 'P1', 'P2', etc.
                measurement_channels = {
                    1: ('C4', 'pkpk'),
                }
        """

        meas_desc = {
            'source'     : 0,
            'measurement': 1
        }

        # --- Turn off all measurements ---
        for sweep_measurements in range(1, 9):
            self.scope.write('VBS app.Measure.P{0}.View=False'.format(sweep_measurements))

        # --- Turn on all listed measurements and set up ---
        for k, v in meas_dict.items():
            self.scope.write('VBS app.Measure.P{0}.View=True'.format(k))
            self.scope.write('VBS app.Measure.P{0}.Source1="{1}"'.format(k, v[meas_desc['source']]))
            self.scope.write('VBS app.Measure.P{0}.ParamEngine="{1}"'.format(k, v[meas_desc['measurement']]))

    def measurement_levelatx(self, meas_channel='1', position=0.0):
        self.scope.write('VBS app.Measure.P{0}.operator.horvalue={1}'.format(meas_channel,position))

    def getValueOnChannel(self, assigned_channel, stat_type='value'):
        """
        Description:
            Get value on assigned channel
            e.g. getValueOnChannel('P1', 'value')

        Arguments:
            :param assigned_channel:
                'P1', 'P2',..
            :param stat_type:
                'value'
                'level@X' - the level at time X (default is 0.0ns)
                'mean'
                'max'
                'min'
                'num'    - number of measurements
                'sdev'   - standard deviation
                'status' - last measurement was valid?

        Return:
            Measurement results for the argument specified
        """
        meas = {'value' : ('app.Measure.{0}.Out.Result.Value'.format(assigned_channel)),
                'mean'  : ('app.Measure.{0}.Statistics("mean").Result.Value'.format(assigned_channel)),
                'max'   : ('app.Measure.{0}.Statistics("max").Result.Value'.format(assigned_channel)),
                'min'   : ('app.Measure.{0}.Statistics("min").Result.Value'.format(assigned_channel)),
                'num'   : ('app.Measure.{0}.Statistics("num").Result.Value'.format(assigned_channel)),
                'sdev'  : ('app.Measure.{0}.Statistics("sdev").Result.Value'.format(assigned_channel)),
                'status': ('app.Measure.{0}.Statistics("last").Result.StatusDescription'.format(assigned_channel))}
        msg = self.scope.query("VBS? return = {0}".format(meas[stat_type]))
        # I had to add this because sometimes scope answers with "VBS *" and sometimes not
        msg = msg[4:] if "VBS" in msg else msg

        if stat_type == 'status' or 'No Data' in msg:
            return msg
        else:
            return float(msg)

    def setGrid(self, gridmode='Single'):
        """
        Sets the number grids on the display.
        :param gridmode: possible values: 'Single', 'Dual', 'Quad', 'Octal', 'Tandem', 'Quattro', 'Auto'
        :return: None
        """
        self.scope.write('VBS app.Display.GridMode="{}"'.format(gridmode))

    def setHorizontal_delay(self, delay=0.0):
        self.scope.write('VBS app.Acquisition.Horizontal.HorOffset={0}'.format(delay))

    def reset_scope(self):
        self.scope.write('*RST')

    def set_intensity(self, percent=100):
        self.scope.write('VBS app.Display.PersistenceSaturation= {0}'.format(percent))

