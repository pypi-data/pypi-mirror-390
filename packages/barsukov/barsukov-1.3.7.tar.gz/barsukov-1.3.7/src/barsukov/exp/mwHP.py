### BEGIN Dependencies ###
import numpy as np
import sys
from barsukov.exp.exp_utils import *
### END Dependencies


class mwHP:
    def __init__(self, gpib=None, visa_rm=None, logger=None, gpib_card=0, log='default', script=None):
        # Pass the Script object, if available.
        # If Script has no visa_rm or if no Script is passed, you'll need to pass the visa_rm=visa.ResourceManager manually.
        # If Script has no logger or if no Script is passed, you can pass the logger manually.
        # If no logger is passed, will simply print to screen.
        # Change log from 'default' to 'screen', 'file', 'both', 'no'.
        # gpib_card is per default 0. You can change, if you have multiple.

        self.script = script
        self.logger = logger
        self.eq_default_log = log
        self.rm = visa_rm
        self.gpib_card = gpib_card
        self.gpib = gpib

        self.msg_deco = f'[mwHP {self.gpib_card}::{self.gpib}]'
        self.eq = initialize_gpib(self) # This will initialize self.eq = visa.open_resource()
        self.log( f'Initialized: {self.identify()}', log='important' ) # This is the 'welcome message' and a check if communication works.

        self.f_digits = 9 # Digits of precision of mw frequency
        self.f_limits = [0.01, 20.5] # Lower and upper GHz limits
        self.p_digits = 1 # Digits of precision of mw power
        self.p_limits = [-15.0, 17.0] # Lower and upper dBm limits
        self.phase_limits = [0.0, 360.0]
        self.pulsef_limits = [0.016, 500]
        self.pulsedc_limits = [0, 100] # Lower and upper % limits


### BEGIN The definition of the following functions may be specific to this equipment.
    def query(self, cmd):
        return self.eq.query(cmd)

    def write(self, cmd):
        return self.eq.write(cmd)

    def identify(self):
        return str(self.eq.query('*IDN?'))
### END The definition of the following functions may be specific to this equipment.
    def disconnect(self):
        eq_disconnect(self)

    def reconnect(self):
        eq_reconnect(self)

    def log(self, msg, log=None):
        if log is None: log=self.eq_default_log
        log_in_eq(self, msg, log=log)
### END These functions could be shared across all equipment.


### BEGIN: mwHP Functions:
    def output(self, state=None, log=None, check=False):
    ### Always has a return! Which is the state of Output.
    ### output() reads and returns the state of Output.
    ### output(1) writes state of Output to ON.
    ### output(1) returns the state that was actually sent to equipment.
    ### output(1, check=True) returns the state queried after writing
        if log is None: log=self.eq_default_log
        if state is None:
            try:
                y = self.eq.query('output?')
                y = int(y)         
                self.log(f'Output is {y}.')
                return y
            except:
                self.log(f'Error while reading Output.', log='important')
                return np.nan
        else:
            if (state == 1) or (state == 'on') or (state=='ON') or (state=='On'): sstate = 1
            else: sstate = 0
            try:
                self.eq.write(f'output {sstate}')
                if check: y=self.output(log='no')
                else: y = sstate
                if y == state: self.log(f'Output set to {sstate}.')
                else: self.log(f'Warning: Setting Output to {sstate}, but was asked for {state}.')
                return y
            except:
                self.log(f'Error while changing Output state.', log='important')
                return np.nan


    def f(self, f=None, log=None, check=False):
    ### Always has a return! Which is frequency in GHz.
    ### f() reads and returns the frequency in GHz.
    ### f(10) writes frequency to 10 GHz.
    ### f(10) returns the frequency that was actually sent to equipment.
    ### f(10, check=True) returns the frequency queried after writing.
    ### Do set log='no' to avoid latency for repeated calls. 
        if log is None: log=self.eq_default_log
        if f is None: 
            try:
                y = self.eq.query('freq?')
                y = float(y)/1e9 # Is the frequency returned in GHz??
                self.log(f'Reading f as {y} GHz.', log=log)
                return y
            except:
                self.log(f'Error while reading Frequency.', log='important')
                return np.nan
        else:
            try:
                x = round(f, self.f_digits) # rounding the digits
                x = max(self.f_limits[0], min(x, self.f_limits[1])) # sets x within f_limits
                self.eq.write(f'freq {x} GHz')
                if check: y = self.f(log='no')
                else: y = x
                if abs(y-f)<10.0**(-self.f_digits): self.log(f'Writing f as {x}.', log=log)
                else: self.log(f'Warning: writing Frequency as {x}, but was asked {f}.', log='important')
                return y
            except:
                self.log(f'Error while writing Frequency as {f}.', log='important')
                return np.nan


    def p(self, p=None, log=None, check=False):
    ### Always has a return! Which is the power in dBm.
    ### p() reads and returns the power in dBm.
    ### p(1) writes power to 1 dBm.
    ### p(1) returns the power that was actually sent to equipment.
    ### p(1, check=True) returns the power queried after writing
    ### Do set log='no' to avoid latency for repeated calls.
        if log is None: log=self.eq_default_log
        if p is None:
            try:
                y = self.eq.query('pow?')
                y = float(y)
                self.log(f'Reading p as {y} dBm.', log=log)
                return y
            except:
                self.log(f'Error while reading Power.', log='important')
                return np.nan
        else:
            try:
                x = round(p, self.p_digits) # rounding the digits
                x = max(self.p_limits[0], min(x, self.p_limits[1])) # sets x within p_limits
                self.eq.write(f'pow {x} dBm')
                if check: y = self.p(log='no')
                else: y = x
                if abs(y-p)<10**(-self.p_digits): self.log(f'Writing p as {x}.', log=log)
                else: self.log(f'Warning: writing Power as {x}, but was asked {p}.', log='important')
                return y
            except:
                self.log(f'Error while writing Power as {p}.', log='important')
                return np.nan


    def sweep(self, start, stop, step, dwell, mode, log=None):
        if log is None: log=self.eq_default_log
        units, write_start, write_stop, mode = '', start, stop, mode.lower()
        if (mode == 'freq') or (mode == 'frequency') or (mode == 'f'): 
            write_start = max(self.f_limits[0], min(write_start, self.f_limits[1]))
            write_stop = max(self.f_limits[0], min(write_stop, self.f_limits[1]))
            mode = 'Frequency'
            units = 'GHz'
        if (mode == 'pow') or (mode == 'power') or (mode == 'p'): 
            write_start = max(self.p_limits[0], min(write_start, self.p_limits[1]))
            write_stop = max(self.p_limits[0], min(write_stop, self.p_limits[1]))
            mode = 'Power'
            units = 'dBm'
        if (write_start != start):
            self.log(f'Warning: Writing {mode} Sweep start to {write_start} but was asked {start}.', log='important')
        if (write_stop != stop): 
            self.log(f'Warning: Writing {mode} Sweep stop to {write_stop} but was asked {stop}.', log='important')
        try:
            self.log(f'{mode} Sweep parameters are start: {write_start} {units}, stop: {write_stop} {units}, step: {step} {units}, dwell: {dwell} s.', log=log)
            self.log(f'Initiating {mode} Sweep: ', log=log)
            from time import sleep
            for point in np.arange(write_start, write_stop+(step/2.0), step):
                if mode == 'Frequency': 
                    self.f(f=point)
                elif mode == 'Power': 
                    self.p(p=point)
                sleep(dwell)
            self.log(f'{mode} Sweep completed.', log=log)
        except:
            self.log(f'Error while conducting Sweep.', log='important')
            return np.nan


    def pulse(self, f=None, duty=None, log=None):
        if log is None: log=self.eq_default_log
        if f is None and duty is None:
            try:
                T = float(self.eq.query('puls:per?')) * 10.0**3
                f = 1.0 / T
                w = float(self.eq.query('puls:widt?')) * 10.0**3
                duty = w / T * 100.0
                y = self.eq.query('pulm:stat?')
                y = int(y)
                x = self.eq.query('pulm:sour?')
                x = x[:-1].lower()
                self.log(f'Pulse Frequency {f} KHz, duty-cycle {duty}%. state {y}, source {x}.', log=log)
                return f, duty
            except:
                self.log(f'Error while reading Pulse state.', log='important')
                return np.nan
        else:
            if duty is None: duty = 50.0
            try:
                if f is None and duty != 50.0:
                    duty_write = max(self.pulsedc_limits[0], min(float(duty), self.pulsedc_limits[1]))
                    T = float(self.eq.query('puls:per?')) * 10.0**3
                    w = duty_write * T / 100.0
                    self.eq.write(f'puls:widt {w} ms')
                elif f is not None and duty == 50.0:
                    f_write = max(self.pulsef_limits[0], min(float(f), self.pulsef_limits[1]))
                    duty_write = duty
                    T = 1.0 / f_write
                    w = duty_write * T / 100.0
                    self.eq.write(f'puls:per {T} ms')
                    self.eq.write(f'puls:widt {w} ms')
                else:
                    f_write = max(self.pulsef_limits[0], min(float(f), self.pulsef_limits[1]))
                    duty_write = max(self.pulsedc_limits[0], min(float(duty), self.pulsedc_limits[1]))
                    T = 1.0 / f_write
                    w = duty_write * T / 100.0
                    self.eq.write(f'puls:per {T} ms')
                    self.eq.write(f'puls:widt {w} ms')
            except:
                self.log(f'Error while writing pulse frequency as {f} and duty cycle as {duty}', log='important')
                return np.nan
            freal, dutyreal = self.pulse()
            if abs(freal - f) < 0.10*float(f): self.log(f'Writing Pulse Frequency as {freal}.', log=log)
            else: self.log(f'Warning:Writing Pulse Frequency as {freal}, but was asked {f}.', log='important')
            if abs(dutyreal - duty) < 0.03*float(duty): self.log(f'Writing Pulse duty cycle as {dutyreal}.', log=log)
            else: self.log(f'Warning:Writing Pulse duty cycle as {dutyreal}, but was asked {duty}.', log='important')
            return freal, dutyreal
### END: mwHP Functions:


### BEGIN: OBJ2FILE Tools
    # Prepares the Script object for serialization by removing non-seriable attributes (e.g. logger and rm).
        # Returns:
            # dict: A dictionary representing the serializable state of the Script object.
    def __getstate__(self):
        seriable_data = self.__dict__.copy()
        # take the attributes of unseriable data
        if self.script is None: 
            if self.logger is not None:
                seriable_data['logger'] == 'needsrebuild'
                seriable_data['logger_information'] = self.logger.__getargs__()
                seriable_data['logger_information']['start_file'] = False
        else:
            seriable_data['script'] == 'needsrebuild'
            seriable_data['script_information'] = self.script.__getstate__()
        seriable_data['rm'] = None
        seriable_data['eq'] = None
        return seriable_data


    def __setstate__(self, seriable_data):
        from barsukov.script import Script
        from barsukov.logger import Logger
        self.__dict__.update(seriable_data)
        if self.script == 'needsrebuild':
            self.script = Script(**seriable_data['script_information'])
        if self.logger == 'needsrebuild':
            self.logger = Logger(**seriable_data['logger_information'])
        if (self.script is not None):
            self.log(f'I am using Script saved in memory: {self.script.folder_name}.', log='screen')
        elif (self.logger is not None):
            self.log(f'I am using Logger saved in memory: {self.logger.description}.', log='screen')
        eq_reconnect(self)
### END: OBJ2FILE Tools