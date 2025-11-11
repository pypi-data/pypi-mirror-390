### BEGIN Dependencies ###
import os
from barsukov.time import time_stamp
### END Dependencies ###

class Logger:
    """
    Logger class that handles logging to both screen and file with flexible configuration

    The logger is started upon initialization. 
    It can be started with the 'start()' method and can be closed using the 'close()' method
    It is designed to avoid creating multiple Logger instances. Restarting the logger logs to the same file unless the 'full_file_path' is manually changed

    Avaliable log options:
    - 'screen': Logs only to the screen.
    - 'file': Logs only to a file.
    - 'both': Logs to both the screen and file.
    - 'no': Disables logging.

    log level 'important' is used for important logs, typically for internal use with higher priority

    Attributes:
        full_file_path (str): path to the log file (e.g., 'D:/Rundong/Projects/AFM sims/2024-07-06 Autooscillations/text.txt')
        description (str): Description of the log's purpose.
        log_mode (str): Defines the logging mode ('screen', 'file', 'both, or 'no').
        file (file object): Log file object.
        file_error (bool): Flag indicating an error with the file
    """
    ### Don't create multiple Logger objects.
    ### Logger can be opened and closed with start() and close() methods.
    ### Restarting the logger will log to the same file, unless self.full_file_path has been changed by hand.
    ### start=True will start the logger automatically, but be careful
    ### about the full_folder_path=os.getcwd() in init.
    ### Log options are 'screen', 'file', 'both', 'no'. The logger default is 'both'.
    ### The log='important' is for the Logger.log() method only. Try not to use it.
    ### Default hyerarchy is logger-default overriden by object-default overriden by instance.
    ### Instances, that log errors, will usually use 'both'.

### BEGIN: Initializing Tools
    def __init__(self,
        description=None, # Will be passed by Script. If not, write a brief description!
        full_folder_path=os.getcwd(), # Will be passed by Script. If not, specify!
        full_file_path=None, #  Specify only if you want to log into an already existing file.
        log='both', # Logger default will be passed by Script. If not, you may choose to change.
        start_file=True,
        ):

        ### Initializing all variables before setting/getting them
        self.full_file_path = full_file_path # If changed by hand later, needs start() to take effect
        self.description = description # If changed by hand later, needs set_full_file_path and start() to take effect       
        self.log_mode = log # Default log mode can be changed by hand any time, no restart needed.

        if self.full_file_path is not None: self.full_folder_path = None
        else:
            self.full_folder_path = full_folder_path # If changed by hand later, needs set_full_file_path and start() to take effect
            self.set_full_file_path(description=description, full_folder_path=full_folder_path)

        if start_file: self.start_file()
        else: self.file = None

        self.file_error = False 
        # If a problem with file, will be set to True. Just in case for later.
        # If problem is remedied, you need to set file_error to False by hand.

        self.log(f'Logger initialization complete.', log='important')


    def set_full_file_path(self, description=None, full_folder_path=None):
        ### Checking if optional arguments are filled or if defaults are provided ###
        if description is None:
            description = self.description
        if full_folder_path is None:
            full_folder_path = self.full_folder_path

        ### Create a file name like log_timeStamp_description_.txt ###
        if description is not None and description != '':
            description = f"_{description}"
        else:
            description = ''
        file_name = f"log_{time_stamp()}{description}_.txt"
        self.full_file_path = os.path.join(full_folder_path, file_name)


    def start_file(self):
        try:
            self.file = open(self.full_file_path, 'a')
            self.log('Logging file started.', log='important')
        except:
            print(f'{time_stamp()} Logger failed to open the log file \"{self.full_file_path}\".', log='important')


    def close_file(self): # If closed, you'll need to restart before logging.
        self.log('Logger is closing log file.', log='important')
        self.file.close()
        self.file = None
### END: Initializing Tools


### BEGIN: logging Tools
    def decorated_msg(self, msg):
        decorated_msg = time_stamp() + ' ' + msg + '\n'
        return decorated_msg


    def write_to_file(self, msg):
        if self.file:
            #add lock here
            self.file.write(msg)
            ### flushing the log file to make sure it's written ###
            self.file.flush()
            #os.fsync(self.file) ##.fileno()
        else:
            self.file_error = True
            print(f'{time_stamp()} Logger is trying to write to a closed or non-existent file.')


    def log(self, msg, log='default'):
        ### This is the main function. Log options: 'screen', 'file', 'both', 'no', 'default', 'important'
        if log == 'important' and self.log_mode == 'no':
            log = 'screen'
        elif log == 'important' and self.log_mode == 'file':
            log = 'both'
        elif (log == 'important') or (log == 'default') or (log is None):
            log = self.log_mode

        decorated_message = self.decorated_msg(msg)

        if log == 'both':
            print(self.decorated_msg(msg))
            self.write_to_file(decorated_message)
        elif log == 'file':
            self.write_to_file(decorated_message)
        elif log == 'no':
            pass
        else: # log == 'screen' or anything else
            print(decorated_message)
### END: logging Tools


### BEGIN: OBJ2FILE TOOLS:
    def __getargs__(self):
        logger_args = self.__getstate__()
        del logger_args['log_mode']
        del logger_args['file_error']
        del logger_args['file']
        return logger_args

    def __getstate__(self):
        seriable_data = self.__dict__.copy()
        return seriable_data
### BEGIN: OBJ2FILE TOOLS:


### Use this function in other libraries if needed for debugging -- Not really needed
DEBUG = False
def debug(msg):
    if DEBUG:
        print(msg)
        return msg+'\n'
    else:
        return msg
###