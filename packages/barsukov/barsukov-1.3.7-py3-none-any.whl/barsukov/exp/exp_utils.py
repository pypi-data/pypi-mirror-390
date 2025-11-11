### BEGIN Dependencies ###
import numpy as np
import sys
from barsukov.time import *
### END Dependencies


### BEGIN Helper functions

def log_in_eq(eq_obj, msg, log='default'): # FINISHED 2024/10/26
    decorated_msg = str(eq_obj.msg_deco) + ' ' + msg
    if eq_obj.logger is None:
        if log=='no': return
        else: print(time_stamp() + ' ' + decorated_msg)
    else:
        eq_obj.logger.log(decorated_msg, log)


def initialize_gpib(eq_obj):
    # Initializes a visa.open_resource(). Returns rm.open_resource(). Exits if error.
    if eq_obj.rm is None: # eq_obj has no ResourceManager
        if eq_obj.script is None:  # If there is no Script
            eq_obj.log('Visa ResourceManager and Script have not been passed to me. I will attempt to initialize visa myself.', log='important')
            try:
                import pyvisa as visa
                eq_obj.rm = visa.ResourceManager()
                eq_obj.log('I just set my self.rm = visa.ResourceManager.', log='screen')
            except:
                eq_obj.log('I failed to initialize set my self.rm = visa.ResourceManager. I am sys-exiting.', log='important')
                sys.exit()
        else: # If there is a Script
            if eq_obj.script.rm is None: # If Script has no ResourceManager
                eq_obj.log('I see Script but it does not have rm. I am asking Script to initialize visa.ResourceManager and pass it to me.', log='important')
                try: 
                    eq_obj.rm = eq_obj.script.init_rm() # Script will try to init ResourceManager
                    #print('eq_obj.rm initialized as ', eq_obj.rm)
                except:
                    eq_obj.log('Error while Script was initializing visa.ResourceManager. I am sys-exiting.', log='important')
                    sys.exit()
            else:
                eq_obj.log('Script has visa.ResourceManager. I am grabbing it.', log='screen')
                eq_obj.rm = eq_obj.script.rm
            if eq_obj.rm is None: # Just to double check if rm is in fact there.
                eq_obj.log('My last check showed that my self.rm is still None. I am sys-exiting.', log='important')
                sys.exit()
    # Now, we assume there is a resource manager
    if (eq_obj.gpib is None) or (eq_obj.gpib_card is None):
        eq_obj.log('GPIB card number or GPIB address is not set.', log='important')
        sys.exit()
    try:
        #print(eq_obj.rm)
        eq_obj.log('I am trying to rm.open_resource().', log='screen')
        y = eq_obj.rm.open_resource(f'GPIB{eq_obj.gpib_card}::{eq_obj.gpib}')
        #print('y=',y)
        return y
    except:
        eq_obj.log(f'I could not initialize rm.open_resource() for GPIB {eq_obj.gpib_card}::{eq_obj.gpib}. Also check visa_rm, just in case.', log='important')
        sys.exit()


def eq_disconnect(eq_obj):
    try:
        eq_obj.rm.close()
        eq_obj.rm.visalib._registry.clear()
        eq_obj.log( f'Successfully disconnected GPIB resource for {eq_obj.gpib_card}::{eq_obj.gpib}.', log='screen')
    except:
        eq_obj.log( f'Failed to disconnect GPIB resource for {eq_obj.gpib_card}::{eq_obj.gpib}.', log='screen')


def eq_reconnect(eq_obj):
    try:
        import pyvisa as visa
        eq_obj.rm = visa.ResourceManager()
        eq_obj.eq = initialize_gpib(eq_obj)
        eq_obj.log( f'Successfully reconnected GPIB resource for {eq_obj.gpib_card}::{eq_obj.gpib}.', log='screen')
        eq_obj.log( f'Initialized: {eq_obj.identify()}', log='important' )
    except: 
        eq_obj.log(f'Failed to reconnect GPIB resource for {eq_obj.gpib_card}::{eq_obj.gpib}.', log='important')

### END Helper functions























### BEGIN Functions that are likely unnecessary

def query_float(eq_obj, cmd):
    ### Returns float or np.nan
    try:
        q = eq_obj.eq.query(cmd)
        q = float(q) # Will it work with all equipment?
        return q
    except:
        eq_obj.log(f'Error while quering: \"{cmd}\".', log='important')
        return np.nan

def write_float(eq_obj, cmd, value, digits, limits):
    value_differs = ''
    try:
        value = float(value)
        value_round = round(value, digits)
        if value_round < limits[0]:
            value_round = limits[0]
        if value_round > limits[1]:
            value_round = limits[1]
        if value_round != value:
            value_differs = f' But requested {value}.'
        cmd = ''.join( [value_round if el is None else el for el in cmd] )
        eq_obj.eq.write(cmd)
        write_error = False
        return write_error, value_differs
    except:
        write_error = True
        eq_obj.log(f'Error while writing: \"{cmd}\".', log='important')
        return write_error, value_differs

### END Functions that are likely unnecessary
