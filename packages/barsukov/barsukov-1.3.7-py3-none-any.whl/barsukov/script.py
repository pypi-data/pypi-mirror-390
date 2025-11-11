### BEGIN Dependencies ###
import sys
import os
from barsukov.time import *
from barsukov.logger import Logger
### END Dependencies


class Script():
    """
    A class that represents a scientific experiment script, managing logging, file handing, and device initialization.

    Args:
        RECOMMENDED:
        operator (str): The name of the operator (default: 'Anon').
        station (str): The station of the experiment (default: 'No-Station').
        sample (str): The sample being tested (default: 'No-Sample').
        description (str): A brief description of the experiment (default: 'No-Description').
        project_folder (str): The base folder for the project files (default: current directory).

        OPTIONAL:
        log (str, optional): The logging configuration (default: 'both')
            This is the default log setting which will be passed to the logger.
            It will be overriden by other objects, which in turn will be overriden by methods.
            Choose here and everywhere from 'screen', 'file', 'both', 'no'.

        BEST NOT TO CHANGE:
        log_full_folder_path (str, optional): Path to save logs (default: current directory).
        log_full_file_path (str, optional): Full path for log file (default: None).

    Attributes:
        operator (str): The operator's name (e.g., 'ib', 'Rundong', 'Sasha', 'Ameerah', 'Steven', 'Alex', or 'AlexH' if ambiguous).
        station (str): The station where the experiment is conducted (e.g., 'qd', 'ppms', 'mseppms', 'data', 'orange', ...).
        sample (str): The sample being used in the experiment (e.g. 'cro2410a1').
        description (str): A brief description of the experiment (e.g., 'Testing modulation').
        project_folder (str): Absolute path to the directory (e.g., 'D:/Rundong/Projects/AFM sims/2024-07-06 Autooscillations').
        folder_name (str): A generated folder name based on the experiment details.
        full_folder_path (str): The full path to the experiment folder.
        logger (Logger): A Logger instance for logging experiment data.
        rm (ResourceManager or None): The pyvisa ResourceManager used for controlling instruments.
    """
### BEGIN: Initializing tools
    def __init__(self, 
        operator='Anon',
        station='No-Station',
        sample='No-Sample',
        description='No-Description',
        project_folder = os.getcwd(),
        log='both', 
        log_full_folder_path=os.getcwd(),
        log_full_file_path=None, 
        ):

        ### Description Attributes
        self.operator = operator
        self.station = station
        self.sample = sample
        self.description = description
        self.project_folder = project_folder

        ### Creating the sub-project folder
        self.folder_name = f"{date()}_{self.station}_{self.operator}_{self.sample}_{self.description}"
        self.full_folder_path = os.path.join(self.project_folder, self.folder_name)
        os.makedirs(self.full_folder_path, exist_ok=True)

        ### Logger Attributes
        self.log_mode = log
        self.log_full_folder_path = log_full_folder_path
        self.log_full_file_path = log_full_file_path
        self.init_logger(start=True)
        self.logger_name = self.logger.full_file_path

        ### Equipment Attributes
        self.rm = None
        self.equipment = None

    def init_logger(self, start):
        ### Starting the logger
        self.logger = Logger(
            description=f"{self.operator}_{self.description}",
            full_folder_path=self.log_full_folder_path,
            full_file_path=self.log_full_file_path,
            log=self.log_mode, # Script.log becomes Logger's default
            start_file=start)
        self.logger.log(f'Script object initialized. Logger started.', log='both')


    def log(self, msg, log='default'):
        """
        Logs a message using the Script object's logger.

        Args:
            msg (str): The message to log.
            log (str, optional): The log destination (e.g., 'screen', 'file', 'both'). Defaults to the 'default' of the logger
        """
        self.logger.log(msg, log=log)
### END: Initializing tools


### BEGIN: Equipment related stuff
    def init_rm(self):
        # Initializes the pyvisa ResourceManager for controlling instruments.
        # Returns ResourceManager The pyvisa ResourceManager object.
        # Raises SystemExit If pyvisa cannot be imported or the ResourceManager cannot be initialized.
        self.equipment = True
        import pyvisa as visa
        try: 
            self.rm = visa.ResourceManager()
        except:
            self.rm = None
            self.log('Script could not import pyvisa.', log='important')
            sys.exit()
        self.log(f'Script started pyvisa.ResourceManager.', log='both')
        return self.rm
### END: Equipment related stuff


### BEGIN: Equipment devices
    def mwHP(self, gpib=None, **kwargs):
        """
        Initializes and returns a mwHP equipment object with the specified parameters.

        Args:
            gpib (str): gpib number of equipment. Defaults to 'None'.
            **kwargs: Additional keyword arguments passed to the mwHP equipment initialization.

        Returns:
            mwHP: A mwHP equipment object.
        """
        from barsukov.exp.mwHP import mwHP as eq
        return eq(gpib, logger=self.logger, script=self, **kwargs)

    def smKE(self, gpib=None, **kwargs):
        """
        Initializes and returns a mwHP equipment object with the specified parameters.

        Args:
            gpib (str): gpib number of equipment. Defaults to 'None'.
            **kwargs: Additional keyword arguments passed to the mwHP equipment initialization.

        Returns:
            mwHP: A mwHP equipment object.
        """
        from barsukov.exp.smKE import smKE as eq
        return eq(gpib, logger=self.logger, script=self, **kwargs)
### END: Equipment devices


### BEGIN: OBJ2FILE TOOLS:
    def __getstate__(self):
        # Prepares the Script object for serialization by removing non-seriable attributes (e.g. logger and rm).
        # Returns a dict: A dictionary representing the serializable state of the Script object.
        seriable_data = self.__dict__.copy()
        del seriable_data['logger']
        del seriable_data['rm']
        return seriable_data


    def __setstate__(self, seriable_data):
        # Restores the Script object from its serialized state, including reinitializing the logger and rm.
        # Args: seriable_data (dict): A dictionary representing the serialized state of the Script object
        self.__dict__.update(seriable_data)
        self.init_logger(start=False)
        if self.equipment is True: self.init_rm()
### END: OBJ2FILE TOOLS: