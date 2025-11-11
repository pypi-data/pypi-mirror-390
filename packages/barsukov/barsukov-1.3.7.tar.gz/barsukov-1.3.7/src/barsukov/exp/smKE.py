### BEGIN Dependencies ###
import numpy as np
import sys
from barsukov.exp.exp_utils import *
### END Dependencies


class smKE:
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

        self.msg_deco = f'[smKE {self.gpib_card}::{self.gpib}]'
        self.eq = initialize_gpib(self) # This will initialize self.eq = visa.open_resource()
        self.log( f'Initialized: {self.identify()}', log='important' ) # This is the 'welcome message' and a check if communication works.
        
        # Digits, x_Min, x_Max, Range_min, Range_max, units, function
        self.I_params = [10, -1.05, 1.05, 1e-6, 1, 'A', 'curr']
        self.V_params = [10, -210.0, 210.0, 0, 210.0, 'V', 'volt'] #digits and range undetermined
        self.R_params = [10, 0.0, 2.1e8, 'R'] #digits undetermined

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
### END These functions could be shared across all equipment.\

    def source(self, function=None, scale=None, level=None, cmpl_scale=None, cmpl_level=None, log=None):
        if log is None: log=self.eq_default_log
        if function is None:
            try:
                f = self.eq.query('sour:func?')
                f = str(f)[:-1]

                s = self.eq.query(f'sour:{f}:rang?')
                s = float(s) / 1.05
                exp = np.floor(np.log10(abs(s)))
                s = np.ceil(s / 10**exp) * 10**exp

                l = self.eq.query(f'sour:{f}:lev?')
                l = float(l)

                if f == 'CURR': source_param, compliance_param = self.I_params, self.V_params
                if f == 'VOLT': source_param, compliance_param = self.V_params, self.I_params

                cs = self.eq.query(f'sens:{source_param[6]}:rang?')
                cs = float(cs)

                cl = self.eq.query(f'sens:{source_param[6]}:prot?')
                cl = float(cl)

                self.log(f'Source function is {f}, scale is {s} {source_param[5]}, level is {l} {source_param[5]}. Compliance scale is {cs} {compliance_param[5]}, level is {cl} {compliance_param[5]}')
                return f, s, l, cs, cl

            except:
                self.log(f'Error while reading source function.', log='important')
                return np.nan
        else:
            if (function == 'curr') or (function == 'current'): source_param, compliance_param = self.I_params, self.V_params
            else: source_param, compliance_param,  = self.V_params, self.I_params
            try:
                if level > scale: level = scale #level must be equal to or less than scale
                if cmpl_level > cmpl_scale: cmpl_level = cmpl_scale

                f = source_param[6]
                self.eq.write(f'sour:func {f}')
                self.eq.write(f'sour:{f}:mode fix')

                s = max(source_param[3], min(float(scale), source_param[4]))
                self.eq.write(f'sour:{f}:rang {s}')

                l = max(source_param[1], min(float(level), source_param[2]))
                self.eq.write(f'sour:{f}:lev {l}')

                cs = max(compliance_param[3], min(float(cmpl_scale), compliace_param[4]))
                self.eq.write(f'sens:{compliance_param[6]}rang:auto off')
                self.eq.write(f'sens:{compliance_param[6]}:rang: {cs}')

                cl = max(compliance_param[1], min(float(cmpl_level), compliance_param[2]))
                self.eq.write(f'sens:{compliance_param[6]}:prot:rsyn on')
                self.eq.write(f'sens:{compliance_param[6]}:prot {cmpl_level}')

                freal, sreal, lreal, csreal, clreal = self.source()
                return freal, sreal, lreal, csreal, clreal

            except:
                self.log(f'Error while changing Source.', log='important')
                return np.nan

    def measure(self, function=None, four_wire=None, res_mode=None, res_guard=None, res_compensation=None, log=None):
        if log is None: log=self.eq_default_log
        if function is None:
            try:
                f = self.eq.query('sens:func?')
                f = str(f)[:-1]

                ws = self.eq.query('syst:rsen?')
                ws = float(ws)
                if ws: ws = 'on'
                else: ws = 'off'

                #self.log(f'Measure function

                if 'RES' in f:
                    rm = self.eq.query('res:mode?')
                    rm = str(f)[:-1]

                    rg = self.eq.query('syst:guard?')
                    rg = str(f)[:-1]

                    rc = self.eq.query('res:ocom?')
                    if ws: ws = 'on'
                    else: ws = 'off'

            except:
                return 0

        self.eq.write(f'sens:func:off:all')
        self.eq.write(f'sens:func:on "{function}"')
        self.eq.write(f'{function}:mode {source}')
        self.eq.write(f'syst:rsen {sense_mode}')
        self.eq.write(f'syst:guard {guard}')